from flask import Flask, request, Response

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
    print(command,text, channel_id)
    return Response(status=200)

    # # Handle different commands
    # if command == '/hello':
    #     return handle_hello_command(text, user_id, channel_id)
    # elif command == '/help':
    #     return handle_help_command()
    # # Add more command handlers as needed

    # # Default response if command is not recognized
    # return Response(
    #     'Command not recognized. Try /help for available commands.',
    #     status=200,
    #     mimetype='application/json'
    # )
def handle_mention(event):
    text = event.get('text')
    channel = event.get("channel")
    ts = event.get("ts")

    def reply_thread(message):
        return client.chat_postMessage(
            channel=channel,
            text=message,
            thread_ts=ts
        )
    def upload_file(message,filepath):
        return client.files_upload_v2(
            channels=channel,
            file=filepath,
            initial_comment=message,
            thread_ts=ts
        )

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