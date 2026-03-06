import json

from interactions.BlockInteraction import BlockInteraction
from file_management.delete_clips import delete_all_clips, delete_clip
from file_management.file_read_lock import file_read_lock
from file_management.get_blocks_from_files import get_blocks_from_files
from flask import Flask, request, Response
from interactions.collect_session_or_all_clips import collect_session_or_all
from server_utils import (response_with_status, post_ephemeral_blocks,
                         post_message_to_channel_or_thread, post_public_blocks)

app = Flask(__name__)

_event_bus = None
_state_machine = None


def init_server(event_bus=None, state_machine=None):
    global _event_bus, _state_machine
    _event_bus = event_bus
    _state_machine = state_machine
    app.run(port=3000)


@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.json
    if 'challenge' in data:
        return Response(data['challenge'], status=200, mimetype='text/plain')
    if 'event' in data:
        event = data['event']
        if event.get('type') == 'app_mention':
            return handle_mention(event)
    return response_with_status("Invalid event type")


@app.route('/slack/interact', methods=['POST'])
def slack_interact():
    payload = json.loads(request.form['payload'])
    interaction = BlockInteraction(payload)

    if interaction.action_id == "null":
        return response_with_status("")

    if file_read_lock.locked():
        interaction.update_with_message("I'm busy right now, try again later!")
        return response_with_status("")

    file_read_lock.acquire()

    if interaction.action_id == "refresh":
        try:
            interaction.refresh_blocks()
        except Exception as e:
            interaction.update_with_message(f"Error refreshing blocks: {e}")
        finally:
            file_read_lock.release()
        return response_with_status("")

    if interaction.action_id == "dismiss":
        try:
            interaction.update_with_message("Okay!")
        finally:
            file_read_lock.release()
        return response_with_status("")

    if interaction.action_id == "delete-all":
        try:
            delete_all_clips()
            interaction.update_with_message("Deleted all clips!")
        except Exception as e:
            interaction.update_with_message(f"Error deleting all clips: {e}")
        finally:
            file_read_lock.release()
        return response_with_status("")

    if interaction.action_id == "delete-clip":
        try:
            delete_clip(interaction.button_value)
            interaction.refresh_blocks()
        except Exception as e:
            interaction.update_with_message(f"Error deleting clip: {e}")
        finally:
            file_read_lock.release()
        return response_with_status("")

    if interaction.action_id == "collect-all":
        try:
            collect_session_or_all(interaction, collect_all=True)
        except Exception as e:
            file_read_lock.release()
            interaction.update_with_message(f"Error collecting all clips: {e}")
        return response_with_status("")

    if interaction.action_id == "collect-session":
        try:
            collect_session_or_all(interaction, collect_all=False)
        except Exception as e:
            file_read_lock.release()
            interaction.update_with_message(f"Error collecting session: {e}")
        return response_with_status("")

    return response_with_status("Interact")


@app.route('/slack/command', methods=['POST'])
def slack_commands():
    from event_bus import EventType

    data = request.form
    command_text = data.get('text', '').strip().lower()

    if data['command'] == '/hl':
        if command_text in ('record', 'start') and _event_bus:
            _event_bus.emit(EventType.SLACK_START)
            return response_with_status('Starting recording.')

        if command_text == 'stop' and _event_bus:
            _event_bus.emit(EventType.SLACK_STOP)
            return response_with_status('Stopping recording.')

        if command_text == 'clip' and _event_bus:
            _event_bus.emit(EventType.SLACK_CLIP)
            return response_with_status('Saving clip.')

        if command_text == 'status' and _state_machine:
            return response_with_status(f'Status: {_state_machine.state.name}')

        is_public = command_text == 'public'
        blocks = get_blocks_from_files()
        if is_public:
            post_public_blocks(data['channel_id'], blocks)
        else:
            post_ephemeral_blocks(data['channel_id'], blocks, data['user_id'])
        return response_with_status('')

    return response_with_status('Command not recognized. Try /help for available commands.')


def handle_mention(event):
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

    return Response(status=200)


if __name__ == "__main__":
    init_server()
