import json
from datetime import datetime
from subprocess import DEVNULL, call
from video_utils import VIDEO_BUFFER_FILE
from audio_utils import AUDIO_BUFFER_FILE


def encode_video(audio_start_time, video_start_time):
    with open("camera_config.json") as f:
        fps = json.load(f)["fps"]
    timestamp = datetime.now().strftime("%Y-%m-%d-%H_%M_%S")
    output_file = f'clips/{timestamp}.mp4'

    if audio_start_time:
        offset = int((audio_start_time - video_start_time) * 1000)
        return call([
            'ffmpeg',
            '-r', str(fps),
            '-i', VIDEO_BUFFER_FILE,
            '-i', AUDIO_BUFFER_FILE,
            '-c:v', 'copy',
            '-af', f'adelay={offset}',
            '-c:a', 'aac', '-ac', '1',
            output_file,
            '-y', '-shortest',
        ], stdout=DEVNULL, stderr=DEVNULL)

    return call([
        'ffmpeg',
        '-r', str(fps),
        '-i', VIDEO_BUFFER_FILE,
        '-c:v', 'copy',
        '-an',
        output_file,
        '-y',
    ], stdout=DEVNULL, stderr=DEVNULL)
