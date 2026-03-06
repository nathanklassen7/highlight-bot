import os


def get_sorted_videos():
    if not os.path.isdir("clips"):
        return []
    clips = [f for f in os.listdir("clips") if f.endswith(".mp4")]
    clips.sort()
    return clips
