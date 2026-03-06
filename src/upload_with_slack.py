import os
from typing import Callable

from consts import CLIP_DIRECTORY
from slack_sdk.errors import SlackApiError


def upload_videos_sequentially(upload_file: Callable, file_names: list[str]):
    for file_name in file_names:
        file_path = os.path.join(CLIP_DIRECTORY, file_name)
        try:
            response = upload_file(file_name, file_path)
            print(response)
            os.remove(file_path)
        except SlackApiError as e:
            print(f"Error uploading {file_name}: {e.response['error']}")
            raise
