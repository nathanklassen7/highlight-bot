import threading
import time
from file_management.get_blocks_from_files import get_blocks_from_files
from server_utils import post_file_to_channel_or_thread, post_message_to_channel_or_thread, update_message_with_response_url
from upload_with_slack import upload_videos_sequentially

def start_sending_clips(channel: str, clips: list[str], response_url: str, old_blocks: list[dict]):
    file_count = len(clips)
    message = f"Sending {file_count} clips!" if file_count > 1 else "Sending 1 clip!"
    response = post_message_to_channel_or_thread(channel, message)
    timestamp = response['ts']
    def upload_files_to_thread(message,filepath):
        return post_file_to_channel_or_thread(channel, filepath, message, timestamp)
    def on_complete():
        collected_blocks = []
        for block in old_blocks:
            if block.get("accessory", {}).get("value") == "null":
                block["accessory"] = collected_button
            collected_blocks.append(block)
        update_message_with_response_url(response_url, collected_blocks, "Collected!")
        time.sleep(2)
        new_blocks = get_blocks_from_files()
        update_message_with_response_url(response_url, new_blocks, "Done!")
    threading.Thread(target=upload_videos_sequentially,args=(upload_files_to_thread, clips, on_complete)).start()
    
    


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