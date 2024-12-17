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
        
        sessions = get_sessions(files)

        clip_index = 0
        for session_index, session in enumerate(sessions):
            message += f"*Session {session_index} -----------------------------------------*"
            message += "\n"
            for file_name in session:
                message += f" *|* Highlight {clip_index} - Recorded "
                message += get_clip_age(file_name)
                message += "\n"
                clip_index += 1
            message += "\n"
        return ResponseWithStatus(message)
    except FileNotFoundError:
        return ResponseWithStatus("The directory does not exist.")
    except Exception as e:
        return ResponseWithStatus("An error occurred.")


def get_sessions(files):
    sessions = [[files.pop(0)]]
    for file_name in files:
        if get_time_difference(file_name, sessions[-1][0]) < timedelta(seconds=10):
            sessions[-1].append(file_name)
        else:
            sessions.append([file_name])
    return sessions