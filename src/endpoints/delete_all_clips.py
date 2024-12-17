import os
import threading
from slack_sdk.errors import SlackApiError
from consts import CLIP_DIRECTORY
from get_sorted_videos import get_sorted_videos
from server_utils import ResponseWithStatus, ResponseFunctions
from flask import Response

def delete_clips(response_functions: ResponseFunctions) -> Response:
    file_names = get_sorted_videos()
    total_clips = len(file_names)
    
    if total_clips==0:
        return ResponseWithStatus('No clips saved.')
    
    file_names_to_delete = []
    
    if len(response_functions.params) == 0:
        file_names_to_delete = file_names
        
    for param in response_functions.params:
        try:
            index = int(param)
            if index >= total_clips or index < 0:
                return ResponseWithStatus(f"Clip {index} does not exist!")
            file_names_to_delete.append(file_names[index])
        except:
            return ResponseWithStatus(f"Invalid clip index '{param}'")
        
    try:
        for file_name in file_names_to_delete:
            os.remove(CLIP_DIRECTORY + file_name)
        files_to_delete_count = len(file_names_to_delete)
        if files_to_delete_count == 1:
            return ResponseWithStatus("Deleted 1 clip!")
        else:
            return ResponseWithStatus(f"Deleted {files_to_delete_count} clips!")

    except SlackApiError as e:
        print(f"Error posting message: {e.response['error']}")
        return ResponseWithStatus("Error deleting clips!")