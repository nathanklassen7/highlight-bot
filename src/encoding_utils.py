from datetime import datetime
from subprocess import DEVNULL, call
from video_utils import fps

def encode_video(audio_file, video_file, audio_start_time, video_start_time):
    offset = int((audio_start_time - video_start_time)*1000)
    timestamp = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    output_file = f'clips/{timestamp}.mp4'
    return call([f'ffmpeg -r {fps} -i {video_file} -i {audio_file} -c:v copy -af "adelay={offset}|{offset}" -c:a aac {output_file} -y -shortest'], shell=True,stdout=DEVNULL, stderr=DEVNULL)