import json
import os

from interactions.BlockInteraction import BlockInteraction
from file_management.delete_clips import delete_all_clips, delete_clip
from file_management.file_read_lock import file_read_lock
from file_management.get_blocks_from_files import get_blocks_from_files
from flask import Flask, request, Response
from interactions.collect_session_or_all_clips import collect_session_or_all
from server_utils import (ResponseWithStatus, post_ephemeral_blocks,
                         post_message_to_channel_or_thread, post_public_blocks)

slack_token = os.environ.get('SLACK_BOT_TOKEN')
print(slack_token)

app = Flask(__name__)

@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.json
    if 'challenge' in data:
        return Response(data['challenge'], status=200, mimetype='text/plain')
    if 'event' in data:
        event = data['event']
        if event.get('type') == 'app_mention':
            return handle_mention(event)
    return ResponseWithStatus("Invalid event type")

@app.route('/slack/interact', methods=['POST'])
def slack_interact():
    payload = json.loads(request.form['payload'])
    interaction = BlockInteraction(payload)
    
    if interaction.action_id == "null":
        return ResponseWithStatus("")
    
    if file_read_lock.locked():
        interaction.update_with_message("I'm busy right now, try again later!")
        return ResponseWithStatus("")
    
    file_read_lock.acquire()
    
    if interaction.action_id == "refresh":
        try:
            interaction.refresh_blocks()
        except Exception as e:
            interaction.update_with_message(f"Error refreshing blocks: {e}")
        finally:
            file_read_lock.release()
        return ResponseWithStatus("")
    
    if interaction.action_id == "dismiss":
        try:
            interaction.update_with_message("Okay!")
        finally:
            file_read_lock.release()
        return ResponseWithStatus("")
    
    if interaction.action_id == "delete-all":
        try: 
            delete_all_clips()
            interaction.update_with_message("Deleted all clips!")
        except Exception as e:
            interaction.update_with_message(f"Error deleting all clips: {e}")
        finally:
            file_read_lock.release()
        return ResponseWithStatus("")
    
    if interaction.action_id == "delete-clip":
        try:
            delete_clip(interaction.button_value)
            interaction.refresh_blocks()
        except Exception as e:
            interaction.update_with_message(f"Error deleting clip: {e}")
        finally:
            file_read_lock.release()
        return ResponseWithStatus("")

    if interaction.action_id == "collect-all":
        try:
            collect_session_or_all(interaction, collect_all=True)
        except Exception as e:
            file_read_lock.release()
            interaction.update_with_message(f"Error collecting all clips: {e}")
        return ResponseWithStatus("")
    
    if interaction.action_id == "collect-session":
        try:
            collect_session_or_all(interaction, collect_all=False)
        except Exception as e:
            file_read_lock.release()
            interaction.update_with_message(f"Error collecting session: {e}")
        return ResponseWithStatus("")
    
    return ResponseWithStatus("Interact")

@app.route('/slack/command', methods=['POST'])
def slack_commands():
    data = request.form
    
    if data['command'] == '/hl':
        blocks = get_blocks_from_files()
        is_public = data['text'] == 'public'
        if is_public:
            post_public_blocks(data['channel_id'], blocks)
        else:
            post_ephemeral_blocks(data['channel_id'], blocks, data['user_id'])
        return ResponseWithStatus('')
    return ResponseWithStatus('Command not recognized. Try /help for available commands.')

def handle_mention(event):
    channel = event.get("channel")
    ts = event.get("ts")
    
    message = f"Hey <@{event.get('user')}>!"
    
    post_message_to_channel_or_thread(
        channel=channel,
        text=message,
        thread_ts=ts
    )
    
    return Response(status=200)
    
def init_server():
    app.run(port=3000)
    
if __name__ == "__main__":
    init_server()