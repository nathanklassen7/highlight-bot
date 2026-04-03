import json
import uuid
from subprocess import DEVNULL, call

from camera_config import get_current_preset, read_config
from clip_db import insert_clip
from consts import SNAPSHOT_DIRECTORY
from video_utils import VIDEO_BUFFER_FILE
from audio_utils import AUDIO_BUFFER_FILE

SNAPSHOT_SCALE_WIDTH = 320
SNAPSHOT_QUALITY = 5
SNAPSHOT_INTERVAL = 2


def _get_duration(video_path):
    from subprocess import check_output, CalledProcessError
    try:
        out = check_output([
            'ffprobe', '-v', 'quiet',
            '-show_entries', 'format=duration',
            '-of', 'csv=p=0', video_path,
        ]).decode().strip()
        return float(out) if out and out != 'N/A' else 0
    except (CalledProcessError, ValueError):
        return 0


def _generate_snapshots(clip_id, video_path):
    """Extract a JPEG snapshot every SNAPSHOT_INTERVAL seconds using keyframe seeking."""
    duration = _get_duration(video_path)
    if duration <= 0:
        return []

    filenames = []
    idx = 1
    t = 0.0
    while t < duration:
        snap_name = f"{clip_id}_{idx:03d}.jpg"
        out_path = f"{SNAPSHOT_DIRECTORY}{snap_name}"
        result = call([
            'ffmpeg', '-y',
            '-ss', str(t),
            '-i', video_path,
            '-frames:v', '1',
            '-vf', f'scale={SNAPSHOT_SCALE_WIDTH}:-1',
            '-q:v', str(SNAPSHOT_QUALITY),
            out_path,
        ], stdout=DEVNULL, stderr=DEVNULL)
        if result == 0:
            filenames.append(snap_name)
        idx += 1
        t += SNAPSHOT_INTERVAL

    return filenames


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
        snapshots = _generate_snapshots(clip_id, output_file)
        cfg = read_config()
        preset = get_current_preset(cfg)
        insert_clip(
            clip_id=clip_id,
            filename=filename,
            resolution_preset=preset,
            duration=video_duration,
            snapshots=snapshots,
        )

    return result
