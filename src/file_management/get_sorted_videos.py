import os

def get_sorted_videos():
    if not os.path.isdir("clips"):
        return []
    clips = os.listdir("clips")
    clips.sort()
    return clips