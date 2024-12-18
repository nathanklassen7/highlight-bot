from typing import Optional
from get_clip_age import get_clip_age
from file_management.get_sessions import get_sessions


loading_button = {
    "type": "button",
    "text": {
        "type": "plain_text",
        "text": ":loading2:",
        "emoji": True
    },
    "action_id": "null",
    "value": "null"
}

collected_button = {
    "type": "button",
    "text": {
        "type": "plain_text",
        "text": "Collected! :check:",
        "emoji": True
    },
    "action_id": "null",
    "value": "null",
    "style": "primary"
}

def get_blocks_from_files(currently_collecting: Optional[list[int]] = []):
    blocks = []
    
    sessions = get_sessions()
    if len(sessions) == 0:
        return [{
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": "All clips have been sent!"
                }
                }]
    

    for session_index, session in enumerate(sessions):
        is_collecting = session_index in currently_collecting
        session_number = session_index + 1
        next_block = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*-------------- Session {session_number} --------------*"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Collect session",
                        "emoji": True
                    },
                    "value": str(session_index),
                    "action_id": "collect-session",
                    "style": "primary"
                } if not is_collecting else loading_button
            }
        
        blocks.append(next_block)
        
        for file_name in session:
            clip_title = f"Recorded {get_clip_age(file_name)}"
            next_block = {
                "type": "section",
                "text": {
                        "type": "plain_text",
                        "text": clip_title
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Delete clip",
                        "emoji": True
                    },
                    "value": file_name,
                    "action_id": "delete-clip",
                    "style": "danger"
                } if not is_collecting else loading_button
            }
            blocks.append(next_block)
    if not len(currently_collecting):
        blocks.append(
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Collect all",
                            "emoji": True
                        },
                        "value": "collect-all",
                        "action_id": "collect-all",
                        "style": "primary"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Delete all",
                            "emoji": True
                        },
                        "value": "delete-all",
                        "action_id": "delete-all",
                        "style": "danger"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Dismiss",
                            "emoji": True
                        },
                        "value": "dismiss",
                        "action_id": "dismiss",
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Refresh",
                            "emoji": True
                        },
                        "value": "refresh",
                        "action_id": "refresh",
                    }
                ]
            }
        )
    else:
        blocks.append({
            "type": "actions",
            "elements": [
                loading_button
            ]
        })
    
    return blocks