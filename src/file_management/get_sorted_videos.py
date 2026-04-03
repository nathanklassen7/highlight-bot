from clip_db import get_all_clips


def get_sorted_videos():
    clips = get_all_clips()
    return [c["filename"] for c in clips]
