from clip_db import get_sessions_from_db


def get_sessions():
    db_sessions = get_sessions_from_db()
    return [[clip["filename"] for clip in session] for session in db_sessions]


def get_session_at_index(index: int):
    sessions = get_sessions()
    return sessions[index]
