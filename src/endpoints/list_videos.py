from get_clip_age import get_clip_age
from get_sorted_videos import get_sorted_videos
from server_utils import ResponseWithStatus

def list_videos():
    try:
        # List all files in the directory
        files = get_sorted_videos()
        if len(files) == 0:
            return ResponseWithStatus("No videos saved!")

        message = ''
        
        for index,file_name in enumerate(files):
            # Check if the file has a valid video format
            if file_name.endswith('.mp4'):    
                message += f"Highlight {index} - Recorded "
                message += get_clip_age(file_name)
                message += "\n"
        return ResponseWithStatus(message)
    except FileNotFoundError:
        return ResponseWithStatus("The directory does not exist.")
    except Exception as e:
        return ResponseWithStatus("An error occurred.")
