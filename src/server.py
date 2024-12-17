from flask import Flask, request, Response

from slack_sdk import WebClient
import os
from endpoints.delete_all_clips import delete_clips
from endpoints.list_videos import list_videos
from endpoints.send_all_clips import send_all_clips
from server_utils import ResponseFunctions, ResponseWithStatus
slack_token = os.environ.get('SLACK_BOT_TOKEN')
print(slack_token)

client = WebClient(token=slack_token)

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
    
    client.chat_postMessage(
        channel=channel,
        text=message,
        thread_ts=ts
    )
    
    return Response(status=200)
    
def init_server():
    app.run(port=3000)
    