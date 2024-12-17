from flask import Response
from slack_sdk import WebClient
import os
client = WebClient(token=os.environ.get('SLACK_BOT_TOKEN'))

def ResponseWithStatus(message):
    return Response(message,status=200,mimetype='text/plain')

class ResponseFunctions:
    def __init__(self, form_data):
        self.channel_id = form_data.get('channel_id')
        self.user_id = form_data.get('user_id')
        self.params = form_data.get('text').split()
        self.command = form_data.get('command')

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
        
    def send_message_with_blocks(self, blocks: list, timestamp: str | None = None) -> dict:
        if timestamp is None:
            return client.chat_postEphemeral(
                channel=self.channel_id,
                user=self.user_id,
                blocks=blocks,
            )
        else:
            return client.chat_update(
                channel=self.channel_id,
                ts=timestamp,
                blocks=blocks,
            )
        
    def send_ephemeral(self, message: str) -> dict:
        return client.chat_postEphemeral(
            channel=self.channel_id,
            text=message,
            user=self.user_id,
        )
        
    def upload_file(self, message: str, filepath: str, timestamp: str) -> dict:
        return client.files_upload_v2(
            channels=self.channel_id,
            file=filepath,
            initial_comment=message,
            thread_ts=timestamp
        )


def post_message(channel: str, text: str, thread_ts: str = None):
    return client.chat_postMessage(
        channel=channel,
        text=text,
        thread_ts=thread_ts
    )
    
def get_message(channel: str, timestamp: str):
    return client.conversations_history(
        channel=channel,
        oldest=timestamp,
        limit=1,
        inclusive=True
    )
    
def update_message_blocks(channel: str, timestamp: str, blocks: list):
    return client.chat_update(
        channel=channel,
        ts=timestamp,
        blocks=blocks
    )