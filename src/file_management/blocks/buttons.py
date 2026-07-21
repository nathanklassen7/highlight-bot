def get_collect_session_button(session_index: int):
    return {
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": "Collect session",
                "emoji": True
            },
            "value": str(session_index),
            "action_id": "collect-session",
            "style": "primary"
        }


def get_preview_session_button(session_index: int):
    return {
        "type": "button",
        "text": {
            "type": "plain_text",
            "text": "Preview session",
            "emoji": True
        },
        "value": str(session_index),
        "action_id": "preview-session",
    }


def delete_clip_button(file_name: str):
    return {
        "type": "button",
        "text": {
            "type": "plain_text",
            "text": "Delete clip",
            "emoji": True
        },
        "value": file_name,
        "action_id": "delete-clip",
        "style": "danger"
    }


def preview_clip_button(file_name: str):
    return {
        "type": "button",
        "text": {
            "type": "plain_text",
            "text": "Preview",
            "emoji": True
        },
        "value": file_name,
        "action_id": "preview-clip",
    }
