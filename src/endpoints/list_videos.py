import os
from datetime import datetime

from flask import Response

from get_clip_age import get_clip_age
from get_sorted_videos import get_sorted_videos

def list_videos(reply_thread):
    try:
        # List all files in the directory
        files = get_sorted_videos()
        if len(files) == 0:
            reply_thread("No videos saved!")
            return Response(status=200)

        message = ''
        
        for index,file_name in enumerate(files):
            # Check if the file has a valid video format
            if file_name.endswith('.mp4'):    
                message += f"Highlight {index} - Recorded "
                message += get_clip_age(file_name)
                message += "\n"
        reply_thread(message)
        return Response(status=200)
    except FileNotFoundError:
        print(f"The directory does not exist.")
        return Response(status=500)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return Response(status=500)
