from flask import Flask, request, Response
from typing import Callable

from slack_sdk import WebClient
import os
from endpoints.delete_all_clips import delete_clips
from endpoints.list_videos import list_videos
from endpoints.send_all_clips import send_all_clips
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
    return Response(status=200)

@app.route('/slack/command', methods=['POST'])
def slack_commands():
    data = request.form
    print(data)
    command = data.get('command')
    text = data.get('text')
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    ts = data.get('ts')
    print(data)
    return Response(status=200)
    
    send_message, upload_file, send_ephemeral = build_response_functions(channel_id, ts, user_id)
    params = text.split()
    
    if command == 'hl-collect':
        return send_all_clips(text,send_message,upload_file)
    if command == 'hl-list':
        return list_videos(send_ephemeral)
    if command == 'hl-delete':
        return delete_clips(text,send_message)
    # # Handle different commands
    # if command == '/hello':
    #     return handle_hello_command(text, user_id, channel_id)
    # elif command == '/help':
    #     return handle_help_command()
    # # Add more command handlers as needed

    # Default response if command is not recognized
    return Response(
        'Command not recognized. Try /help for available commands.',
        status=200,
        mimetype='application/json'
    )
def handle_mention(event):
    text = event.get('text')
    channel = event.get("channel")
    ts = event.get("ts")
    user_id = event.get("user")
    reply_thread, upload_file = build_response_functions(channel, ts, user_id)

    params = text.split()
    
    command = params[1]
    # Check if the message contains a specific command
    if command == 'collect':
        params = params[2:]
        return send_all_clips(params,reply_thread,upload_file)
    if command == 'list':
        return list_videos(reply_thread)
    if command == 'delete':
        params = params[2:]
        return delete_clips(params,reply_thread)
    reply_thread("Invalid command!")
    return Response(status=200)
    
def init_server():
    app.run(port=3000)
    
def build_response_functions(channel_id: str, timestamp: str, user_id: str) -> tuple[
    Callable[[str], dict],  # reply_thread type
    Callable[[str, str], dict]  # upload_file type
]:
    def reply_thread(message: str) -> dict:
        return client.chat_postMessage(
            channel=channel_id,
            text=message,
            thread_ts=timestamp
        )
        
    def send_message(message:str)  -> dict:
        return client.chat_postMessage(
            channel=channel_id,
            text=message,
            thread_ts=timestamp
        )
        
    def send_ephemeral(message:str) -> dict:
        return client.chat_postEphemeral(
            channel=channel_id,
            text=message,
            user=user_id
        )
        
    def upload_file(message: str, filepath: str) -> dict:
        return client.files_upload_v2(
            channels=channel_id,
            file=filepath,
            initial_comment=message,
            thread_ts=timestamp
        )
    return reply_thread, upload_file