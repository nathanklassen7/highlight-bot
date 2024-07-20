
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

client = WebClient(token=SLACK_BOT_TOKEN)

def upload_video(filename):
    try:
        response = client.files_upload(
            channels=SLACK_CHANNEL_ID,
            file=filename,
            initial_comment="Here's the latest 30 seconds of footage!"
        )
        print(response)
    except SlackApiError as e:
        print(f"Error uploading file: {e.response['error']}")

def handle_message(event_data):
    message_text = event_data['text']
    if '/highlight' in message_text:
        # Save buffered frames to a video file
        out = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc(*'XVID'), 30, (640, 480))
        for frame in video_buffer:
            out.write(frame)
        out.release()

        # Upload the saved video file to Slack
        upload_video('output.avi')