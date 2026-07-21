"""Create highly compressed preview MP4s (480p, 24fps)."""

import logging
import subprocess
import uuid
from pathlib import Path

from consts import CLIP_DIRECTORY

logger = logging.getLogger(__name__)

PREVIEW_HEIGHT = 480
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


def _run_ffmpeg(cmd: list[str], output_path: str) -> str:
    logger.info("Creating preview: %s", output_path)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("ffmpeg preview failed: %s", result.stderr)
        raise RuntimeError(
            f"ffmpeg failed: {result.stderr[-500:] if result.stderr else 'unknown error'}"
        )
    return output_path


def make_clip_preview(input_path: str) -> str:
    """Compress a single clip to 480p/24fps. Caller must delete the returned path."""
    if not Path(input_path).is_file():
        raise FileNotFoundError(f"Clip file not found: {input_path}")

    output_path = f"{CLIP_DIRECTORY}preview_{uuid.uuid4().hex}.mp4"
    keep_audio = _has_audio_stream(input_path)
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", f"scale=-2:{PREVIEW_HEIGHT},fps={PREVIEW_FPS}",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", str(PREVIEW_CRF),
    ]
    if keep_audio:
        cmd += ["-c:a", "aac", "-b:a", PREVIEW_AUDIO_BITRATE, "-ac", "1"]
    else:
        cmd.append("-an")
    cmd.append(output_path)
    return _run_ffmpeg(cmd, output_path)


def make_session_preview(filenames: list[str]) -> str:
    """Stitch session clips and compress to 480p/24fps. Caller must delete the returned path."""
    if not filenames:
        raise ValueError("No clips in session")

    paths = [f"{CLIP_DIRECTORY}{name}" for name in filenames]
    for path in paths:
        if not Path(path).is_file():
            raise FileNotFoundError(f"Clip file not found: {path}")

    if len(paths) == 1:
        return make_clip_preview(paths[0])

    n = len(paths)
    has_audio = [_has_audio_stream(p) for p in paths]
    keep_audio = all(has_audio)
    output_path = f"{CLIP_DIRECTORY}preview_{uuid.uuid4().hex}.mp4"

    cmd = ["ffmpeg", "-y"]
    for path in paths:
        cmd += ["-i", path]

    filter_parts: list[str] = []
    concat_inputs: list[str] = []
    vf = f"scale=-2:{PREVIEW_HEIGHT},fps={PREVIEW_FPS},setpts=PTS-STARTPTS"

    if keep_audio:
        for i in range(n):
            filter_parts.append(f"[{i}:v]{vf}[v{i}]")
            filter_parts.append(
                f"[{i}:a]asetpts=PTS-STARTPTS[a{i}]"
            )
            concat_inputs.append(f"[v{i}][a{i}]")
        filter_parts.append(
            f"{''.join(concat_inputs)}concat=n={n}:v=1:a=1[outv][outa]"
        )
        filter_complex = ";".join(filter_parts)
        cmd += [
            "-filter_complex", filter_complex,
            "-map", "[outv]", "-map", "[outa]",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", str(PREVIEW_CRF),
            "-c:a", "aac", "-b:a", PREVIEW_AUDIO_BITRATE, "-ac", "1",
            output_path,
        ]
    else:
        for i in range(n):
            filter_parts.append(f"[{i}:v]{vf}[v{i}]")
            concat_inputs.append(f"[v{i}]")
        filter_parts.append(
            f"{''.join(concat_inputs)}concat=n={n}:v=1:a=0[outv]"
        )
        filter_complex = ";".join(filter_parts)
        cmd += [
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", str(PREVIEW_CRF),
            "-an",
            output_path,
        ]

    return _run_ffmpeg(cmd, output_path)
