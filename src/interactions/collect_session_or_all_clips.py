import threading
import time
import interactions.BlockInteraction as BlockInteraction
from file_management.get_sorted_videos import get_sorted_videos
from file_management.get_sessions import get_session_at_index
from file_management.get_blocks_from_files import convert_to_collected, get_blocks_from_files
from upload_with_slack import upload_videos_sequentially
from typing import Optional
from file_management.file_read_lock import file_read_lock

def collect_session_or_all(interaction: BlockInteraction, collect_all: Optional[bool] = False):
    in_progress_blocks = []
    files_to_send = []
    
    if collect_all:
        in_progress_blocks = get_blocks_from_files(currently_collecting="all")
        files_to_send = get_sorted_videos()
    else:
        session_index = int(interaction.button_value)
        in_progress_blocks = get_blocks_from_files(currently_collecting=session_index)
        files_to_send = get_session_at_index(session_index)
    
    interaction.update_blocks(in_progress_blocks, "Collecting...")
    
    file_count = len(files_to_send)

    interaction.start_thread(f"Sending {file_count} clips!" if file_count > 1 else "Sending 1 clip!")
    
    def upload_files_to_thread(message,filepath):
        return interaction.post_file_in_thread(filepath, message)
    
    def on_complete():
        file_read_lock.release()
        collected_blocks = convert_to_collected(in_progress_blocks)
        interaction.update_blocks(collected_blocks, "Collected!")
        time.sleep(2)
        interaction.refresh_blocks()

    threading.Thread(target=upload_videos_sequentially,args=(upload_files_to_thread, files_to_send, on_complete)).start()