from flask import Flask, request, Response

from slack_sdk import WebClient
import os

from endpoints.list_videos import list_videos
from endpoints.send_all_clips import send_all_clips
slack_token = os.environ.get('SLACK_BOT_TOKEN')

client = WebClient(token=slack_token)

app = Flask(__name__)

@app.route('/slack/events', methods=['POST'])
def slack_events():
    print('request')
    data = request.json
    if 'challenge' in data:
        return Response(data['challenge'], status=200, mimetype='text/plain')
    if 'event' in data:
        event = data['event']
        if event.get('type') == 'app_mention':
            return handle_mention(event)

    return Response(status=200)

def handle_mention(event):
    text = event.get('text')
    channel = event.get("channel")
    ts = event.get("ts")
    print(text)

    def reply_thread(message):
        return client.chat_postMessage(
            channel=channel,
            text=message,
            thread_ts=ts
        )

    # Check if the message contains a specific command
    if 'collect' in text:
        return send_all_clips(client,event,reply_thread)
    if 'list' in text:
        return list_videos(reply_thread)
    
def init_server():
    app.run(port=3000)
    

if __name__ == '__main__':
    init_server()