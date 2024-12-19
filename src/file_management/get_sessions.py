
from datetime import timedelta
from file_management.get_sorted_videos import get_sorted_videos
from get_clip_age import get_time_difference


def get_sessions():
    # List all files in the directory
    files = get_sorted_videos()
    if len(files) == 0:
        return []
    
    sessions = [[files[0]]]
    for file_name in files[1:]:
        if get_time_difference(file_name, sessions[-1][-1]) < timedelta(minutes=10):
            sessions[-1].append(file_name)
        else:
            sessions.append([file_name])
    return sessions

def get_session_at_index(index: int):
    sessions = get_sessions()
    return sessions[index]