import json
from datetime import datetime, timedelta
from subprocess import DEVNULL, call
from video_utils import VIDEO_BUFFER_FILE
from audio_utils import AUDIO_BUFFER_FILE


def encode_video(audio_start_time, video_start_time, video_duration):
    with open("camera_config.json") as f:
        fps = json.load(f)["fps"]
    timestamp = datetime.now().strftime("%Y-%m-%d-%H_%M_%S")
    one_second_later = datetime.now() + timedelta(seconds=1)
    timestamp_alt = one_second_later.strftime("%Y-%m-%d-%H_%M_%S")
    output_file = f'clips/{timestamp}.mp4'
    alt_output_file = f'clips/{timestamp_alt}.mp4'

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
        return call(cmd, stdout=DEVNULL, stderr=DEVNULL)

    return call([
        '-y',
        'ffmpeg',
        '-r', str(fps),
        '-i', VIDEO_BUFFER_FILE,
        '-c:v', 'copy',
        '-an',
        output_file,
    ], stdout=DEVNULL, stderr=DEVNULL)
