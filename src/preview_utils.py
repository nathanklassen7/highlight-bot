"""Create highly compressed preview MP4s (360p, 24fps, ultrafast)."""

import logging
import subprocess
import uuid
from pathlib import Path

from consts import CLIP_DIRECTORY

logger = logging.getLogger(__name__)

PREVIEW_HEIGHT = 360
PREVIEW_FPS = 24
PREVIEW_CRF = 32
PREVIEW_AUDIO_BITRATE = "64k"


def _has_audio_stream(path: str) -> bool:
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-select_streams",
                "a",
                "-show_entries",
                "stream=index",
                "-of",
                "csv=p=0",
                path,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        return bool(result.stdout.strip())
    except OSError:
        return False


def make_clip_preview(input_path: str) -> str:
    """Compress a clip to 360p/24fps with ultrafast preset. Caller deletes path."""
    if not Path(input_path).is_file():
        raise FileNotFoundError(f"Clip file not found: {input_path}")

    output_path = f"{CLIP_DIRECTORY}preview_{uuid.uuid4().hex}.mp4"
    keep_audio = _has_audio_stream(input_path)
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", f"scale=-2:{PREVIEW_HEIGHT},fps={PREVIEW_FPS}",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", str(PREVIEW_CRF),
    ]
    if keep_audio:
        cmd += ["-c:a", "aac", "-b:a", PREVIEW_AUDIO_BITRATE, "-ac", "1"]
    else:
        cmd.append("-an")
    cmd.append(output_path)

    logger.info("Creating preview: %s", output_path)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("ffmpeg preview failed: %s", result.stderr)
        raise RuntimeError(
            f"ffmpeg failed: {result.stderr[-500:] if result.stderr else 'unknown error'}"
        )
    return output_path
