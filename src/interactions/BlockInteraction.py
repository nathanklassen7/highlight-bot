from file_management.get_blocks_from_files import get_blocks_from_files
from server_utils import post_file_to_channel_or_thread, post_message_to_channel_or_thread, update_message_with_response_url

class BlockInteraction:
    def __init__(self, payload: dict):
        self.response_url = payload['response_url']
        action = payload['actions'][0]
        self.action_id = action['action_id']
        self.button_value = action['value']
        self.channel_id = payload['container']['channel_id']
        self.thread_ts = None

    def update_blocks(self, blocks: list, message: str):
        update_message_with_response_url(self.response_url, blocks, message)
        
    def refresh_blocks(self):
        new_blocks = get_blocks_from_files()
        self.update_blocks(new_blocks, "Refreshed!")
    
    def update_with_message(self, message: str):
        update_message_with_response_url(self.response_url, [], message)
    
    def start_thread(self,message: str):
        response = post_message_to_channel_or_thread(self.channel_id, message)
        self.thread_ts = response['ts']
    
    def post_file_in_thread (self, filepath: str, message: str):
        post_file_to_channel_or_thread(self.channel_id, filepath, message, self.thread_ts)