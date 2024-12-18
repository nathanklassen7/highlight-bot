
from typing import Callable, Optional
from consts import CHANNEL_ID, CLIP_DIRECTORY
from slack_sdk.errors import SlackApiError
import os

def upload_videos_sequentially(upload_file, file_names, onComplete: Optional[Callable] = None):
    try:
        for file_name in file_names:
            file_path = CLIP_DIRECTORY + file_name
            response = upload_file(file_name, file_path)
            print(response)
            os.remove(file_path) 
        if onComplete:
            onComplete()
    except SlackApiError as e:
        print(f"Error uploading file: {e.response['error']}")