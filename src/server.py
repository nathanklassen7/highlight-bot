import logging
import os
import re
import subprocess
import threading

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from clip_db import ClipPrefixError, resolve_clip_prefix
from consts import CLIP_DIRECTORY
from edit_utils import EditSegment, SLOWMO_SPEED, stitch_segments
from interactions.BlockInteraction import BlockInteraction
from file_management.delete_clips import delete_all_clips, delete_clip
from file_management.file_read_lock import file_read_lock
from file_management.get_blocks_from_files import get_blocks_from_files
from interactions.collect_session_or_all_clips import collect_session_or_all
from interactions.preview_clips import preview_clip, preview_session
from server_utils import (post_ephemeral_blocks,
                         post_message_to_channel_or_thread, post_public_blocks,
                         post_file_to_channel_or_thread)
from video_utils import capture_frame
from camera_config import build_config_blocks, update_field, reset_config, EDITABLE_FIELDS, PRESETS, apply_preset
from event_bus import State

logger = logging.getLogger(__name__)

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

_event_bus = None
_state_machine = None

# id start-end  OR  id start-replayStart-replayEnd-end
EDIT_SEGMENT_RE = re.compile(
    r"([0-9a-f]{8,})\s+"
    r"(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)"
    r"(?:-(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?))?"
)
EDIT_USAGE = (
    "Usage: /hl edit <id> <start>-<end> "
    "or <id> <start>-<replayStart>-<replayEnd>-<end> ..."
)


def _reboot_system():
    try:
        subprocess.run(['sudo', 'reboot'], check=True)
    except Exception as e:
        logger.error('Reboot failed: %s', e)


def _parse_edit_segments(edit_body: str) -> list[EditSegment]:
    matches = list(EDIT_SEGMENT_RE.finditer(edit_body))
    if not matches:
        raise ValueError(EDIT_USAGE)

    # Reject leftover tokens that aren't part of a valid segment pair
    consumed = EDIT_SEGMENT_RE.sub(" ", edit_body)
    leftover = consumed.strip()
    if leftover:
        raise ValueError(f"Could not parse: {leftover}\n{EDIT_USAGE}")

    segments: list[EditSegment] = []
    for match in matches:
        prefix = match.group(1)
        t0, t1 = float(match.group(2)), float(match.group(3))
        clip = resolve_clip_prefix(prefix)
        path = f"{CLIP_DIRECTORY}{clip['filename']}"

        if match.group(4) is not None:
            # Four timestamps: start-replayStart-replayEnd-end
            replay_start, end = t1, float(match.group(5))
            replay_end = float(match.group(4))
            start = t0
            if start < 0 or end <= start:
                raise ValueError(
                    f"Invalid range {match.group(2)}-{match.group(5)} for {prefix[:8]}"
                )
            if replay_start < 0 or replay_end <= replay_start:
                raise ValueError(
                    f"Invalid replay range {match.group(3)}-{match.group(4)} "
                    f"for {prefix[:8]}"
                )
            if replay_start < start or replay_end > end:
                raise ValueError(
                    f"Replay {match.group(3)}-{match.group(4)} must be within "
                    f"{match.group(2)}-{match.group(5)} for {prefix[:8]}"
                )
            segments.append(EditSegment(path=path, start=start, end=end, speed=1.0))
            segments.append(
                EditSegment(
                    path=path,
                    start=replay_start,
                    end=replay_end,
                    speed=SLOWMO_SPEED,
                )
            )
        else:
            start, end = t0, t1
            if start < 0 or end <= start:
                raise ValueError(
                    f"Invalid range {match.group(2)}-{match.group(3)} for {prefix[:8]}"
                )
            segments.append(EditSegment(path=path, start=start, end=end, speed=1.0))
    return segments


def _run_edit_and_upload(channel_id: str, user_id: str, segments: list[EditSegment]):
    output_path = None
    try:
        output_path = stitch_segments(segments)
        post_file_to_channel_or_thread(channel_id, output_path, "Edited highlight")
    except Exception as e:
        logger.error("Edit failed: %s", e)
        post_ephemeral_blocks(
            channel_id,
            [{
                "type": "section",
                "text": {"type": "plain_text", "text": f"Edit failed: {e}"},
            }],
            user_id,
        )
    finally:
        if output_path and os.path.isfile(output_path):
            try:
                os.unlink(output_path)
            except OSError as e:
                logger.error("Failed to delete temp edit file %s: %s", output_path, e)


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
        if _state_machine and _state_machine.state == State.RECORDING:
            _event_bus.emit(EventType.SLACK_CLIP)
            message = "Saving clip!"
        else:
            message = "I'm sleeping! use /hl record to start recording."
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
        if _state_machine and _state_machine.state == State.RECORDING:
            _event_bus.emit(EventType.SLACK_CLIP)
            ack('Saving clip.')
        else:
            ack("I'm sleeping! use /hl record to start recording.")
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
        if len(parts) == 2:
            _, preset_or_key = parts
            if preset_or_key in PRESETS:
                try:
                    apply_preset(preset_or_key)
                    ack(f'Applied preset: {preset_or_key}')
                except ValueError as e:
                    ack(f'Error: {e}')
                return
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
        preset_names = ', '.join(PRESETS.keys())
        ack(f'Usage: /hl config <preset> or /hl config <key> <value>\nPresets: {preset_names}')
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

    if command_text == 'reboot':
        ack('Rebooting!')
        threading.Timer(1.0, _reboot_system).start()
        return

    if command_text == 'ids':
        ack()
        blocks = get_blocks_from_files(include_ids=True)
        post_ephemeral_blocks(channel_id, blocks, user_id)
        return

    if command_text == 'edit' or command_text.startswith('edit '):
        edit_body = command_text[4:].strip()
        if not edit_body:
            ack(EDIT_USAGE)
            return
        try:
            segments = _parse_edit_segments(edit_body)
        except (ValueError, ClipPrefixError) as e:
            ack(str(e))
            return
        ack('Editing highlight…')
        threading.Thread(
            target=_run_edit_and_upload,
            args=(channel_id, user_id, segments),
            daemon=True,
        ).start()
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

    if interaction.action_id == "preview-clip":
        try:
            preview_clip(interaction)
        except Exception as e:
            file_read_lock.release()
            interaction.update_with_message(f"Error previewing clip: {e}")
        return

    if interaction.action_id == "preview-session":
        try:
            preview_session(interaction)
        except Exception as e:
            file_read_lock.release()
            interaction.update_with_message(f"Error previewing session: {e}")
        return

    file_read_lock.release()
    logger.warning(f"Unhandled action_id: {interaction.action_id}")
