from typing import Optional, Union
from file_management.blocks.action_row import action_row
from file_management.blocks.buttons import delete_clip_button, get_collect_session_button
from get_clip_age import get_clip_age
from file_management.get_sessions import get_sessions
from file_management.blocks.placeholder_buttons import loading_button, collected_button
def get_blocks_from_files(currently_collecting: Optional[Union[int, str]] = None):
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
        next_block = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*-------------- Session {session_number} --------------*"
                },
                "accessory": get_collect_session_button(session_index) if not is_collecting else loading_button
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
                "accessory": delete_clip_button(file_name) if not is_collecting else loading_button
            }
            blocks.append(next_block)
    if currently_collecting is None:
        blocks.append(action_row)
    else:
        blocks.append({
            "type": "actions",
            "elements": [
                loading_button
            ]
        })
    
    return blocks

def convert_to_collected(blocks: list[dict]):
    new_blocks = []
    for block in blocks:
        if block.get("accessory", {}).get("value") == "loading":
            block["accessory"] = collected_button
        elif block.get("elements", [{}])[0].get("value","") == "loading":
            block = action_row
        new_blocks.append(block)
    return new_blocks