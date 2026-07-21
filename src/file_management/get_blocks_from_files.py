from pathlib import Path
from typing import Optional, Union

from file_management.blocks.action_row import action_row
from file_management.blocks.buttons import (
    delete_clip_button,
    get_collect_session_button,
    get_preview_session_button,
    preview_clip_button,
)
from file_management.blocks.placeholder_buttons import collected_button, loading_button
from file_management.get_sessions import get_sessions
from get_clip_age import get_clip_age


def _actions_row(elements: list[dict]) -> dict:
    return {"type": "actions", "elements": elements}


def get_blocks_from_files(
    currently_collecting: Optional[Union[int, str]] = None,
    include_ids: bool = False,
):
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
        is_collecting = session_index == currently_collecting or currently_collecting == "all"
        session_number = session_index + 1
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*-------------- Session {session_number} --------------*"
            },
        })
        if is_collecting:
            blocks.append(_actions_row([loading_button]))
        else:
            blocks.append(_actions_row([
                get_collect_session_button(session_index),
                get_preview_session_button(session_index),
            ]))

        for file_name in session:
            age = get_clip_age(file_name)
            if include_ids:
                clip_id = Path(file_name).stem[:8]
                clip_title = f"{clip_id} · Recorded {age}"
            else:
                clip_title = f"Recorded {age}"
            blocks.append({
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": clip_title
                },
            })
            if is_collecting:
                blocks.append(_actions_row([loading_button]))
            else:
                blocks.append(_actions_row([
                    preview_clip_button(file_name),
                    delete_clip_button(file_name),
                ]))

    if currently_collecting is None:
        blocks.append(action_row)
    else:
        blocks.append(_actions_row([loading_button]))

    return blocks


def convert_to_collected(blocks: list[dict]):
    new_blocks = []
    last_index = len(blocks) - 1
    for i, block in enumerate(blocks):
        if block.get("type") == "actions":
            elements = block.get("elements", [])
            if elements and elements[0].get("value") == "loading":
                if i == last_index:
                    new_blocks.append(action_row)
                else:
                    new_blocks.append(_actions_row([collected_button]))
                continue
        new_blocks.append(block)
    return new_blocks
