import json
from file_management.get_blocks_from_files import get_blocks_from_files
from file_management.get_sessions import get_sessions
from flask import Flask, request, Response

import os
from file_management.delete_clips import delete_all_clips, delete_clip 
from file_management.send_all_clips import start_sending_clips
from server_utils import ResponseWithStatus, post_ephemeral_blocks, post_message_to_channel_or_thread, post_public_blocks, update_message_with_response_url
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
    
    # Extract common useful information
    user_id = payload['user']['id']
    action = payload['actions'][0]  # Get the first action (button click)
    
    # Get specific action details
    action_id = action['action_id']
    button_value = action['value']
    # Get the original message info
    channel_id = payload['container']['channel_id']
    
    if action_id == "null":
        return ResponseWithStatus("")
    
    if action_id == "delete-all":
        delete_all_clips()
        new_blocks = get_blocks_from_files()
        update_message_with_response_url(payload['response_url'], new_blocks, "Deleted all clips!")
        return ResponseWithStatus("")

    if action_id == "collect-all":
        sessions = get_sessions()
        collecting_indices = [i for i in range(len(sessions))]
        in_progress_blocks = get_blocks_from_files(currently_collecting=collecting_indices)
        files_to_send = [file_name for session in sessions for file_name in session]
        update_message_with_response_url(payload['response_url'], in_progress_blocks, "Collecting...")
        start_sending_clips(channel_id, files_to_send, payload['response_url'], in_progress_blocks)
        return ResponseWithStatus("")
    
    if action_id == "refresh":
        new_blocks = get_blocks_from_files()
        update_message_with_response_url(payload['response_url'], new_blocks, "Refreshed!")
        return ResponseWithStatus("")
    
    if action_id == "dismiss":
        update_message_with_response_url(payload['response_url'],[], "Okay!")
        return ResponseWithStatus("")
    
    if action_id == "collect-session":
        session_index = int(button_value)
        print(f"Collecting session {session_index}")
        files_to_send = get_sessions()[session_index]
        in_progress_blocks = get_blocks_from_files(currently_collecting=[session_index])
        update_message_with_response_url(payload['response_url'], in_progress_blocks, "Collecting...")
        start_sending_clips(channel_id, files_to_send, payload['response_url'], in_progress_blocks)
        return ResponseWithStatus("")
    
    if action_id == "delete-clip":
        delete_clip(button_value)
        new_blocks = get_blocks_from_files()
        update_message_with_response_url(payload['response_url'], new_blocks, "Deleted clip!")
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
    text = event.get('text')
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