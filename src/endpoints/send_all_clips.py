import threading
from server import ResponseFunctions
from server_utils import ResponseWithStatus
from slack_sdk.errors import SlackApiError
from flask import Response
from get_sorted_videos import get_sorted_videos
from upload_with_slack import upload_videos_sequentially

def send_all_clips(response_functions: ResponseFunctions):
    file_names = get_sorted_videos()
    total_clips = len(file_names)
    
    if total_clips==0:
        return ResponseWithStatus("No clips saved.")
    
    file_names_to_send = []
    
    if len(response_functions.params) == 0:
        file_names_to_send = file_names
        
    for param in response_functions.params:
        try:
            index = int(param)
            if index >= total_clips or index < 0:
                return ResponseWithStatus(f"Clip {index} does not exist!")
            file_names_to_send.append(file_names[index])
        except:
            return ResponseWithStatus(f"Invalid clip index '{param}'")
        
    try:
        file_count = len(file_names_to_send)
        message = f"Sending {file_count} clips!" if file_count > 1 else "Sending 1 clip!"
        response = response_functions.send_message(message)
        thread_ts = response['ts']
        def upload_files_to_thread(message,filepath):
            return response_functions.upload_file(message,filepath,thread_ts)
        threading.Thread(target=upload_videos_sequentially,args=(upload_files_to_thread, file_names_to_send)).start()
        return Response()
    except SlackApiError as e:
        print(f"Error posting message: {e.response['error']}")
        return ResponseWithStatus("An error occurred.")
