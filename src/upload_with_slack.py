
from consts import CHANNEL_ID, CLIP_DIRECTORY
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from flask import Flask, request, Response
import os
from subprocess import call

from get_sorted_videos import get_sorted_videos

def upload_videos_sequentially(client, channel, ts):
    files = get_sorted_videos()
    
    try:
        for file in files:
            response = client.files_upload_v2(
                channels=channel,
                file=CLIP_DIRECTORY+file,
                initial_comment=file,
                thread_ts=ts
            )
            print(response)
            os.remove(CLIP_DIRECTORY+file)
    except SlackApiError as e:
        print(f"Error uploading file: {e.response['error']}")