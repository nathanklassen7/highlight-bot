import json
import uuid
from subprocess import DEVNULL, call

from camera_config import get_current_preset, read_config
from clip_db import insert_clip
from video_utils import VIDEO_BUFFER_FILE
from audio_utils import AUDIO_BUFFER_FILE


def encode_video(audio_start_time, video_start_time, video_duration):
    with open("camera_config.json") as f:
        fps = json.load(f)["fps"]

    clip_id = uuid.uuid4().hex
    filename = f"{clip_id}.mp4"
    output_file = f"clips/{filename}"

    if audio_start_time:
        offset = int((audio_start_time - video_start_time) * 1000)
        cmd = [
            'ffmpeg',
            '-y',
            '-r', str(fps),
            '-i', VIDEO_BUFFER_FILE,
            '-i', AUDIO_BUFFER_FILE,
            '-c:v', 'copy',
            '-af', f'adelay={offset}',
            '-c:a', 'aac', '-ac', '1',
        ]
        if video_duration:
            cmd += ['-t', str(video_duration)]
        cmd.append(output_file)
        result = call(cmd, stdout=DEVNULL, stderr=DEVNULL)
    else:
        result = call([
            'ffmpeg',
            '-y',
            '-r', str(fps),
            '-i', VIDEO_BUFFER_FILE,
            '-c:v', 'copy',
            '-an',
            output_file,
        ], stdout=DEVNULL, stderr=DEVNULL)

    if result == 0:
        cfg = read_config()
        preset = get_current_preset(cfg)
        insert_clip(
            clip_id=clip_id,
            filename=filename,
            resolution_preset=preset,
            duration=video_duration,
        )

    return result
