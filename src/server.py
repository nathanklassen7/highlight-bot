import os
import re
import logging

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from interactions.BlockInteraction import BlockInteraction
from file_management.delete_clips import delete_all_clips, delete_clip
from file_management.file_read_lock import file_read_lock
from file_management.get_blocks_from_files import get_blocks_from_files
from interactions.collect_session_or_all_clips import collect_session_or_all
from server_utils import (post_ephemeral_blocks,
                         post_message_to_channel_or_thread, post_public_blocks,
                         post_file_to_channel_or_thread)
from video_utils import capture_frame
from camera_config import build_config_blocks, update_field, reset_config, EDITABLE_FIELDS
from event_bus import State

logger = logging.getLogger(__name__)

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

_event_bus = None
_state_machine = None


def init_server(event_bus=None, state_machine=None):
    global _event_bus, _state_machine
    _event_bus = event_bus
    _state_machine = state_machine
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()


@app.event("app_mention")
def handle_mention(event, say):
    channel = event.get("channel")
    ts = event.get("ts")
    text = event.get("text", "").lower()

    from event_bus import EventType

    if "start" in text and _event_bus:
        _event_bus.emit(EventType.SLACK_START)
        message = "Starting recording!"
    elif "stop" in text and _event_bus:
        _event_bus.emit(EventType.SLACK_STOP)
        message = "Stopping recording!"
    elif "clip" in text and _event_bus:
        _event_bus.emit(EventType.SLACK_CLIP)
        message = "Saving clip!"
    elif "status" in text and _state_machine:
        message = f"Status: {_state_machine.state.name}"
    else:
        message = f"Hey <@{event.get('user')}>!"

    post_message_to_channel_or_thread(
        channel=channel,
        text=message,
        thread_ts=ts
    )


@app.command("/hl")
def handle_command(ack, command):
    from event_bus import EventType

    command_text = command.get('text', '').strip().lower()
    channel_id = command['channel_id']
    user_id = command['user_id']

    if command_text in ('record', 'start') and _event_bus:
        _event_bus.emit(EventType.SLACK_START)
        ack('Starting recording.')
        return

    if command_text == 'stop' and _event_bus:
        _event_bus.emit(EventType.SLACK_STOP)
        ack('Stopping recording.')
        return

    if command_text == 'clip' and _event_bus:
        _event_bus.emit(EventType.SLACK_CLIP)
        ack('Saving clip.')
        return

    if command_text == 'pic':
        ack()
        try:
            path = capture_frame()
            post_file_to_channel_or_thread(channel_id, path, '')
        except Exception as e:
            logger.error(f'Error capturing frame: {e}')
        return

    if command_text == 'config':
        ack()
        blocks = build_config_blocks()
        post_ephemeral_blocks(channel_id, blocks, user_id)
        return

    if command_text.startswith('config '):
        if _state_machine and _state_machine.state != State.IDLE:
            ack('Stop recording before editing config.')
            return
        parts = command_text.split(maxsplit=2)
        if len(parts) == 3:
            _, key, value = parts
            if key in EDITABLE_FIELDS:
                try:
                    update_field(key, value)
                    ack(f'Updated {key} to {value}.')
                except (ValueError, TypeError) as e:
                    ack(f'Invalid value: {e}')
                return
            ack(f'Unknown config key: {key}')
            return
        ack('Usage: /hl config <key> <value>')
        return

    if command_text == 'timeout' and _state_machine:
        hours = _state_machine.inactivity_timeout / 3600
        ack(f'Inactivity timeout: {hours:.2f} hours')
        return

    if command_text.startswith('timeout ') and _state_machine:
        try:
            hours = float(command_text.split(maxsplit=1)[1])
            if hours <= 0:
                ack('Timeout must be positive.')
                return
            _state_machine.inactivity_timeout = hours * 3600
            _state_machine.save_timeout()
            ack(f'Inactivity timeout set to {hours:.2f} hours.')
        except ValueError:
            ack('Usage: /hl timeout <hours>')
        return

    if command_text == 'status' and _state_machine:
        ack(f'Status: {_state_machine.state.name}')
        return

    ack()
    is_public = command_text == 'public'
    blocks = get_blocks_from_files()
    if is_public:
        post_public_blocks(channel_id, blocks)
    else:
        post_ephemeral_blocks(channel_id, blocks, user_id)


@app.action(re.compile(".*"))
def handle_interaction(ack, body, action):
    ack()

    interaction = BlockInteraction(body)

    if interaction.action_id == "null":
        return

    if interaction.action_id == "config-dismiss":
        interaction.update_with_message("Okay!")
        return

    if interaction.action_id in ("config-reset",) or \
       interaction.action_id.startswith(("config-edit-", "config-set-")):
        if _state_machine and _state_machine.state != State.IDLE:
            interaction.update_with_message("Stop recording before editing config.")
            return

    if interaction.action_id == "config-reset":
        try:
            reset_config()
            blocks = build_config_blocks()
            interaction.update_blocks(blocks, "Camera config")
        except Exception as e:
            interaction.update_with_message(f"Error resetting config: {e}")
        return

    if interaction.action_id.startswith("config-edit-"):
        key = interaction.action_id.removeprefix("config-edit-")
        if key in EDITABLE_FIELDS:
            field = EDITABLE_FIELDS[key]
            interaction.update_blocks([
                {
                    "type": "input",
                    "dispatch_action": True,
                    "element": {
                        "type": "plain_text_input",
                        "action_id": f"config-set-{key}",
                        "placeholder": {"type": "plain_text", "text": f"Enter {field['label']}"},
                    },
                    "label": {"type": "plain_text", "text": field["label"]},
                }
            ], f"Edit {field['label']}")
        return

    if interaction.action_id.startswith("config-set-"):
        key = interaction.action_id.removeprefix("config-set-")
        if key in EDITABLE_FIELDS:
            value = interaction.button_value
            try:
                update_field(key, value)
                blocks = build_config_blocks()
                interaction.update_blocks(blocks, "Camera config")
            except (ValueError, TypeError) as e:
                interaction.update_with_message(f"Invalid value: {e}")
        return

    if file_read_lock.locked():
        interaction.update_with_message("I'm busy right now, try again later!")
        return

    file_read_lock.acquire()

    if interaction.action_id == "refresh":
        try:
            interaction.refresh_blocks()
        except Exception as e:
            interaction.update_with_message(f"Error refreshing blocks: {e}")
        finally:
            file_read_lock.release()
        return

    if interaction.action_id == "dismiss":
        try:
            interaction.update_with_message("Okay!")
        finally:
            file_read_lock.release()
        return

    if interaction.action_id == "delete-all":
        try:
            delete_all_clips()
            interaction.update_with_message("Deleted all clips!")
        except Exception as e:
            interaction.update_with_message(f"Error deleting all clips: {e}")
        finally:
            file_read_lock.release()
        return

    if interaction.action_id == "delete-clip":
        try:
            delete_clip(interaction.button_value)
            interaction.refresh_blocks()
        except Exception as e:
            interaction.update_with_message(f"Error deleting clip: {e}")
        finally:
            file_read_lock.release()
        return

    if interaction.action_id == "collect-all":
        try:
            collect_session_or_all(interaction, collect_all=True)
        except Exception as e:
            file_read_lock.release()
            interaction.update_with_message(f"Error collecting all clips: {e}")
        return

    if interaction.action_id == "collect-session":
        try:
            collect_session_or_all(interaction, collect_all=False)
        except Exception as e:
            file_read_lock.release()
            interaction.update_with_message(f"Error collecting session: {e}")
        return

    file_read_lock.release()
    logger.warning(f"Unhandled action_id: {interaction.action_id}")
