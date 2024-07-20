import os
import time
import cv2

SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')  # Your bot token here
SLACK_CHANNEL_ID = 'your_channel_id'  # Channel ID where messages are received

# Constants for video capture
VIDEO_DURATION = 30  # Total duration to capture in seconds
VIDEO_BUFFER_SIZE = 900  # Number of frames to keep in buffer (approx 30 seconds at 30 fps)

# Initialize OpenCV capture
cap = cv2.VideoCapture(0)  # Use 0 for the built-in webcam

# Initialize video buffer
video_buffer = []

 from upload_with_slack import handle_message

if __name__ == '__main__':
    start_time = time.time()
    while True:
        ret, frame = cap.read()
        if ret:
            video_buffer.append(frame)
            # Keep only the last VIDEO_BUFFER_SIZE frames (approx 30 seconds)
            if len(video_buffer) > VIDEO_BUFFER_SIZE:
                video_buffer = video_buffer[-VIDEO_BUFFER_SIZE:]

        # Check for Slack messages every second
        if time.time() - start_time > 1:
            try:

        # Check if it's time to save and upload the last 30 seconds
        if time.time() - start_time > VIDEO_DURATION:
            # Save buffered frames to a video file
            out = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc(*'XVID'), 30, (640, 480))
            for frame in video_buffer:
                out.write(frame)
            out.release()

            # Upload the saved video file to Slack
            upload_video('output.avi')

            # Reset start time and clear the buffer
            start_time = time.time()
            video_buffer = []

        # Delay to control the frame rate of the video capture
        time.sleep(0.033)  # Approximately 30 