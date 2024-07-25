import threading
from slack_sdk.errors import SlackApiError
from flask import Response
from get_sorted_videos import get_sorted_videos
from upload_with_slack import upload_videos_sequentially
import os

def send_all_clips(params,reply_thread,upload_file):
    file_names = get_sorted_videos()
    total_clips = len(file_names)
    
    if total_clips==0:
        reply_thread("No clips saved.")
        return Response(status=200)
    
    file_names_to_send = []
    
    if len(params) == 0:
        file_names_to_send = file_names
        
    for param in params:
        try:
            index = int(param)
            if index >= total_clips or index < 0:
                reply_thread(f"Clip {index} does not exist!")
                return Response(status=200)
            file_names_to_send.append(file_names[index])
        except:
            reply_thread(f"Invalid clip index '{param}'")
            return Response(status=200)
        
    try:
        reply_thread(f"Sending {len(file_names_to_send)} clips!")
        threading.Thread(target=upload_videos_sequentially,args=(upload_file, file_names_to_send)).start()
        return Response(status=200)
    except SlackApiError as e:
        print(f"Error posting message: {e.response['error']}")
        return Response(status=500)