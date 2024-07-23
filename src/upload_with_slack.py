
from consts import CHANNEL_ID, CLIP_DIRECTORY
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from flask import Flask, request, Response
import os
from subprocess import call

def upload_all_videos(client, channel, ts):
    files = os.listdir('clips')
    files.sort()
    file_uploads = [{"file":CLIP_DIRECTORY+file,"title":file} for file in files]
    print(file_uploads)
    try:
        response = client.files_upload_v2(
            channels=channel,
            file_uploads=file_uploads,
            initial_comment="Here's the latest 30 seconds of footage!",
            thread_ts=ts
        )
        print(response)
        call([f'rm -rf clips'],shell=True)
    except SlackApiError as e:
        print(f"Error uploading file: {e.response['error']}")
        

def upload_videos_sequentially(client, channel, ts):
    files = [filename for filename in os.listdir('clips')]
    files.sort()
    
    try:
        for file in files:
            response = client.files_upload_v2(
                channels=channel,
                file=CLIP_DIRECTORY+file,
                initial_comment=file,
                thread_ts=ts
            )
            print(response)
        call([f'rm -rf clips'],shell=True)
    except SlackApiError as e:
        print(f"Error uploading file: {e.response['error']}")