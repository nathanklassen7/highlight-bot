"""Stitch trimmed clip segments into a single MP4 via ffmpeg."""

import logging
import subprocess
import uuid
from dataclasses import dataclass
from pathlib import Path

from consts import CLIP_DIRECTORY

logger = logging.getLogger(__name__)


@dataclass
class EditSegment:
    path: str
    start: float
    end: float

    @property
    def duration(self) -> float:
        return self.end - self.start


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


def stitch_segments(segments: list[EditSegment]) -> str:
    """Trim and concat segments into a temp MP4. Caller must delete the returned path."""
    if not segments:
        raise ValueError("At least one segment is required")

    for seg in segments:
        if seg.start < 0 or seg.end <= seg.start:
            raise ValueError(f"Invalid range {seg.start}-{seg.end} for {seg.path}")
        if not Path(seg.path).is_file():
            raise FileNotFoundError(f"Clip file not found: {seg.path}")

    n = len(segments)
    has_audio = [_has_audio_stream(seg.path) for seg in segments]
    keep_audio = all(has_audio)

    output_path = f"{CLIP_DIRECTORY}edit_{uuid.uuid4().hex}.mp4"
    cmd = ["ffmpeg", "-y"]

    for seg in segments:
        cmd += ["-i", seg.path]

    filter_parts: list[str] = []
    concat_inputs: list[str] = []

    if keep_audio:
        for i, seg in enumerate(segments):
            filter_parts.append(
                f"[{i}:v]trim=start={seg.start}:end={seg.end},setpts=PTS-STARTPTS[v{i}]"
            )
            filter_parts.append(
                f"[{i}:a]atrim=start={seg.start}:end={seg.end},asetpts=PTS-STARTPTS[a{i}]"
            )
            concat_inputs.append(f"[v{i}][a{i}]")
        filter_parts.append(
            f"{''.join(concat_inputs)}concat=n={n}:v=1:a=1[outv][outa]"
        )
        filter_complex = ";".join(filter_parts)
        cmd += [
            "-filter_complex",
            filter_complex,
            "-map",
            "[outv]",
            "-map",
            "[outa]",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "23",
            "-c:a",
            "aac",
            "-ac",
            "1",
            output_path,
        ]
    else:
        for i, seg in enumerate(segments):
            filter_parts.append(
                f"[{i}:v]trim=start={seg.start}:end={seg.end},setpts=PTS-STARTPTS[v{i}]"
            )
            concat_inputs.append(f"[v{i}]")
        filter_parts.append(f"{''.join(concat_inputs)}concat=n={n}:v=1:a=0[outv]")
        filter_complex = ";".join(filter_parts)
        cmd += [
            "-filter_complex",
            filter_complex,
            "-map",
            "[outv]",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "23",
            "-an",
            output_path,
        ]

    logger.info("Stitching %d segments -> %s", n, output_path)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("ffmpeg stitch failed: %s", result.stderr)
        raise RuntimeError(f"ffmpeg failed: {result.stderr[-500:] if result.stderr else 'unknown error'}")

    return output_path
