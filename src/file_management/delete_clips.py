import os

from clip_db import get_clip_by_filename, delete_clip_record, get_all_clips, delete_all_clip_records
from consts import CLIP_DIRECTORY, SNAPSHOT_DIRECTORY
from file_management.get_sorted_videos import get_sorted_videos


def _delete_snapshots(filename: str):
    clip = get_clip_by_filename(filename)
    if not clip:
        return
    for snap in clip.get("snapshots", []):
        path = os.path.join(SNAPSHOT_DIRECTORY, snap)
        if os.path.exists(path):
            os.remove(path)


def delete_clip(clip_name: str):
    _delete_snapshots(clip_name)
    path = os.path.join(CLIP_DIRECTORY, clip_name)
    if os.path.exists(path):
        os.remove(path)
    delete_clip_record(clip_name)


def delete_all_clips():
    for clip in get_all_clips():
        for snap in clip.get("snapshots", []):
            path = os.path.join(SNAPSHOT_DIRECTORY, snap)
            if os.path.exists(path):
                os.remove(path)
    file_names = get_sorted_videos()
    for file_name in file_names:
        path = os.path.join(CLIP_DIRECTORY, file_name)
        if os.path.exists(path):
            os.remove(path)
    delete_all_clip_records()
