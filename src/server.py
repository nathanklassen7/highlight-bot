import json
from flask import Flask, request, Response

from slack_sdk import WebClient
import os
from endpoints.delete_all_clips import delete_clips
from endpoints.list_videos import list_videos
from endpoints.send_all_clips import send_all_clips
from server_utils import ResponseFunctions, ResponseWithStatus, get_message, post_message, update_message_blocks
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
    block_id = action['block_id']
    button_value = action['value']
    
    # Get the original message info
    channel_id = payload['container']['channel_id']
    message_ts = payload['container']['message_ts']
    
    print(f"Interact: {action_id} {block_id} {button_value} {channel_id} {message_ts}")
    
    get_message_response = get_message(channel_id, message_ts)
    print(get_message_response)
    original_blocks = get_message_response['messages'][0]['blocks']
    
    new_blocks = original_blocks[1:]
    
    update_message_blocks(channel_id, message_ts, new_blocks)
    
    return ResponseWithStatus("Interact")

@app.route('/slack/command', methods=['POST'])
def slack_commands():
    data = request.form
    response_functions = ResponseFunctions(data)
    
    if response_functions.command == '/hl-list':
        return list_videos(response_functions)
    if response_functions.command == '/hl-collect':
        return send_all_clips(response_functions)
    if response_functions.command == '/hl-delete':
        return delete_clips(response_functions)
    return ResponseWithStatus('Command not recognized. Try /help for available commands.')

def handle_mention(event):
    text = event.get('text')
    channel = event.get("channel")
    ts = event.get("ts")
    
    message = f"Hey <@{event.get('user')}>!"
    
    post_message(
        channel=channel,
        text=message,
        thread_ts=ts
    )
    
    return Response(status=200)
    
def init_server():
    app.run(port=3000)
    
