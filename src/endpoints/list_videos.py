from datetime import timedelta
from get_clip_age import get_clip_age, get_time_difference
from get_sorted_videos import get_sorted_videos
from server_utils import ResponseFunctions, ResponseWithStatus

def list_videos(response_functions: ResponseFunctions, timestamp: str | None = None):
    try:
        # List all files in the directory
        files = get_sorted_videos()
        if len(files) == 0:
            return ResponseWithStatus("No videos saved!")
        
        blocks = []
        
        sessions = get_sessions(files)

        clip_index = 0
        for session_index, session in enumerate(sessions):
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Session {session_index} -----------------------------------------*"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Collect session",
                            "emoji": True
                        },
                        "value": f"session_{session_index}",
                        "action_id": "collect-session"
                    }
                }
            )
            for file_name in session:
                clip_title = f" *|*   Highlight {clip_index} - Recorded {get_clip_age(file_name)}"
                blocks.append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": clip_title
                        },
                        "accessory": {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Collect clip",
                                "emoji": True
                            },
                            "value": f"clip_{clip_index}",
                            "action_id": "collect-clip"
                        }
                    }
                )
                clip_index += 1

        return response_functions.send_message_with_blocks(blocks, timestamp)
    except FileNotFoundError:
        return ResponseWithStatus("The directory does not exist.")
    except Exception as e:
        return ResponseWithStatus("An error occurred.")


def get_sessions(files):
    sessions = [[files[0]]]
    for file_name in files[1:]:
        if get_time_difference(file_name, sessions[-1][0]) < timedelta(seconds=10):
            sessions[-1].append(file_name)
        else:
            sessions.append([file_name])
    return sessions