from slack_sdk.errors import SlackApiError
from flask import Flask, request, Response

from slack_sdk import WebClient
import os

from upload_with_slack import upload_videos_sequentially
import threading 
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
    channel = event.get('channel')
    user = event.get('user')
    ts = event.get("ts")
    print(text)

    # Check if the message contains a specific command
    if 'collect' in text:
        try:
            client.chat_postMessage(
                channel=channel,
                text=f"Working on it!",
                thread_ts=ts
            )
            threading.Thread(target=upload_videos_sequentially,args=(client,channel,ts)).start()
            return Response(status=200)
        except SlackApiError as e:
            print(f"Error posting message: {e.response['error']}")
            return Response(status=500)
            
def init_server():
    app.run(port=3000)
    

if __name__ == '__main__':
    init_server()