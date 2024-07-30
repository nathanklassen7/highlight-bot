import os
import threading
from slack_sdk.errors import SlackApiError
from flask import Response
from consts import CLIP_DIRECTORY
from get_sorted_videos import get_sorted_videos
from upload_with_slack import upload_videos_sequentially

def delete_clips(params, reply_thread):
    file_names = get_sorted_videos()
    total_clips = len(file_names)
    
    if total_clips==0:
        reply_thread("No clips saved.")
        return Response(status=200)
    
    file_names_to_delete = []
    
    if len(params) == 0:
        file_names_to_delete = file_names
        
    for param in params:
        try:
            index = int(param)
            if index >= total_clips or index < 0:
                reply_thread(f"Clip {index} does not exist!")
                return Response(status=200)
            file_names_to_delete.append(file_names[index])
        except:
            reply_thread(f"Invalid clip index '{param}'")
            return Response(status=200)
        
    try:
        for file_name in file_names_to_delete:
            os.remove(CLIP_DIRECTORY + file_name)
        reply_thread(f"Deleted {len(file_names_to_delete)} clips!")
        return Response(status=200)
    except SlackApiError as e:
        print(f"Error posting message: {e.response['error']}")
        return Response(status=500)