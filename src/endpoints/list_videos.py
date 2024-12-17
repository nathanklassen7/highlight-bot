from datetime import timedelta
from get_clip_age import get_clip_age, get_time_difference
from get_sorted_videos import get_sorted_videos
from server_utils import ResponseWithStatus

def list_videos():
    try:
        # List all files in the directory
        files = get_sorted_videos()
        if len(files) == 0:
            return ResponseWithStatus("No videos saved!")

        message = ''
        
        sessions = [[files.pop(0)]]
        for file_name in files:
            if get_time_difference(file_name, sessions[-1][0]) < timedelta(seconds=10):
                sessions[-1].append(file_name)
            else:
                sessions.append([file_name])
                
        print(sessions)
        
        for index,file_name in enumerate(files):
            # Check if the file has a valid video format
            message += f"Highlight {index} - Recorded "
            message += get_clip_age(file_name)
            message += "\n"
        return ResponseWithStatus(message)
    except FileNotFoundError:
        return ResponseWithStatus("The directory does not exist.")
    except Exception as e:
        return ResponseWithStatus("An error occurred.")
