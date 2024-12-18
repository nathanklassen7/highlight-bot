import os
from consts import CLIP_DIRECTORY
from file_management.get_sorted_videos import get_sorted_videos

def delete_clip(clip_name: str):
    os.remove(CLIP_DIRECTORY + clip_name)
    
def delete_all_clips():
    file_names = get_sorted_videos()
    for file_name in file_names:
        os.remove(CLIP_DIRECTORY + file_name)