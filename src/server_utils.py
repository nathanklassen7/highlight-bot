from typing import Optional
import requests
from flask import Response
from slack_sdk import WebClient
import os
client = WebClient(token=os.environ.get('SLACK_BOT_TOKEN'))

def ResponseWithStatus(message):
    return Response(message,status=200,mimetype='text/plain')

def post_message_to_channel_or_thread(channel: str, text: str, thread_ts: Optional[str] = None):
    return client.chat_postMessage(
        channel=channel,
        text=text,
        thread_ts=thread_ts
    )
    
def post_file_to_channel_or_thread(channel: str, filepath: str, message: str, thread_ts: Optional[str] = None):
    return client.files_upload_v2(
        channel=channel,
        file=filepath,
        initial_comment=message,
        thread_ts=thread_ts
    )

def post_ephemeral_blocks(channel: str, blocks: list, user_id: str):
    return client.chat_postEphemeral(
        channel=channel,
        blocks=blocks,
        user=user_id,
        text='Highlights'
    )

def post_public_blocks(channel: str, blocks: list):
    return client.chat_postMessage(
        channel=channel,
        blocks=blocks,
        text='Highlights'
    )

def update_message_with_response_url(response_url: str, blocks: list, message: str):
    return requests.post(response_url, json={"blocks": blocks, "text": message})