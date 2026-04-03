import os

from clip_db import delete_clip_record, delete_all_clip_records
from consts import CLIP_DIRECTORY
from file_management.get_sorted_videos import get_sorted_videos


def delete_clip(clip_name: str):
    path = os.path.join(CLIP_DIRECTORY, clip_name)
    if os.path.exists(path):
        os.remove(path)
    delete_clip_record(clip_name)


def delete_all_clips():
    file_names = get_sorted_videos()
    for file_name in file_names:
        path = os.path.join(CLIP_DIRECTORY, file_name)
        if os.path.exists(path):
            os.remove(path)
    delete_all_clip_records()
