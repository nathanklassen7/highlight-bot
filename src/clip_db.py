import json
import sqlite3
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent.parent / "clips.db"

_local = threading.local()


def _get_conn() -> sqlite3.Connection:
    if not hasattr(_local, "conn") or _local.conn is None:
        _local.conn = sqlite3.connect(str(DB_PATH))
        _local.conn.row_factory = sqlite3.Row
        _local.conn.execute("PRAGMA journal_mode=WAL")
        _local.conn.execute("PRAGMA foreign_keys=ON")
    return _local.conn


def init_db():
    conn = _get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS clips (
            id          TEXT PRIMARY KEY,
            filename    TEXT NOT NULL UNIQUE,
            created_at  TEXT NOT NULL,
            resolution_preset TEXT,
            duration    REAL,
            snapshots   TEXT NOT NULL DEFAULT '[]'
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_clips_created_at ON clips(created_at)
    """)
    conn.commit()


def insert_clip(
    clip_id: str,
    filename: str,
    created_at: Optional[datetime] = None,
    resolution_preset: Optional[str] = None,
    duration: Optional[float] = None,
    snapshots: Optional[list[str]] = None,
):
    conn = _get_conn()
    conn.execute(
        """
        INSERT INTO clips (id, filename, created_at, resolution_preset, duration, snapshots)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            clip_id,
            filename,
            (created_at or datetime.now()).isoformat(),
            resolution_preset,
            duration,
            json.dumps(snapshots or []),
        ),
    )
    conn.commit()


def get_clip(clip_id: str) -> Optional[dict]:
    row = _get_conn().execute("SELECT * FROM clips WHERE id = ?", (clip_id,)).fetchone()
    return _row_to_dict(row) if row else None


def get_clip_by_filename(filename: str) -> Optional[dict]:
    row = _get_conn().execute(
        "SELECT * FROM clips WHERE filename = ?", (filename,)
    ).fetchone()
    return _row_to_dict(row) if row else None


def get_all_clips() -> list[dict]:
    rows = _get_conn().execute(
        "SELECT * FROM clips ORDER BY created_at ASC"
    ).fetchall()
    return [_row_to_dict(r) for r in rows]


def delete_clip_record(filename: str):
    conn = _get_conn()
    conn.execute("DELETE FROM clips WHERE filename = ?", (filename,))
    conn.commit()


def delete_all_clip_records():
    conn = _get_conn()
    conn.execute("DELETE FROM clips")
    conn.commit()


def update_clip_snapshots(filename: str, snapshots: list[str]):
    conn = _get_conn()
    conn.execute(
        "UPDATE clips SET snapshots = ? WHERE filename = ?",
        (json.dumps(snapshots), filename),
    )
    conn.commit()


def get_sessions_from_db(gap_minutes: int = 10) -> list[list[dict]]:
    """Group clips into sessions separated by gaps of `gap_minutes`."""
    clips = get_all_clips()
    if not clips:
        return []

    sessions: list[list[dict]] = [[clips[0]]]
    gap = timedelta(minutes=gap_minutes)

    for clip in clips[1:]:
        prev_time = sessions[-1][-1]["created_at"]
        curr_time = clip["created_at"]
        if curr_time - prev_time < gap:
            sessions[-1].append(clip)
        else:
            sessions.append([clip])

    return sessions


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["created_at"] = datetime.fromisoformat(d["created_at"])
    d["snapshots"] = json.loads(d["snapshots"])
    return d
