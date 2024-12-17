from flask import Flask, request, Response

from slack_sdk import WebClient
import os
from endpoints.delete_all_clips import delete_clips
from endpoints.list_videos import list_videos
from endpoints.send_all_clips import send_all_clips
from server_utils import ResponseWithStatus
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
        return list_videos()
    if response_functions.command == '/hl-collect':
        return send_all_clips(response_functions)
    if response_functions.command == '/hl-delete':
        return delete_clips(response_functions)
    return ResponseWithStatus('Command not recognized. Try /help for available commands.')

def handle_mention(event):
    text = event.get('text')
    channel = event.get("channel")
    ts = event.get("ts")
    user_id = event.get("user")
    
    response_functions = ResponseFunctions({
        'channel_id': channel,
        'ts': ts,
        'user_id': user_id,
        'text': text
    })
    response_functions.reply_thread("Hello!")
    return Response(status=200)
    
def init_server():
    app.run(port=3000)
    
class ResponseFunctions:
    def __init__(self, form_data):
        self.channel_id = form_data.get('channel_id')
        self.user_id = form_data.get('user_id')
        self.params = form_data.get('text').split()
        self.command = form_data.get('command')
        self.timestamp = form_data.get('ts')
        print(self.timestamp)

    def reply_to_thread(self, message: str, timestamp: str) -> dict:
        return client.chat_postMessage(
            channel=self.channel_id,
            text=message,
            thread_ts=timestamp
        )
        
    def send_message(self, message: str) -> dict:
        return client.chat_postMessage(
            channel=self.channel_id,
            text=message,
        )
        
    def send_ephemeral(self, message: str) -> dict:
        return client.chat_postEphemeral(
            channel=self.channel_id,
            text=message,
            user=self.user_id
        )
        
    def upload_file(self, message: str, filepath: str, timestamp: str) -> dict:
        return client.files_upload_v2(
            channels=self.channel_id,
            file=filepath,
            initial_comment=message,
            thread_ts=timestamp
        )
