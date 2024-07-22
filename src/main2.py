import cv2
import time
import threading
import copy
from matplotlib import pyplot as plt
from testcam import activate_camera

# Constants for video capture
VIDEO_DURATION = 30  # Total duration to capture in seconds
VIDEO_BUFFER_SIZE = 200  # Number of frames to keep in buffer (approx 30 seconds at 30 fps)

# Initialize OpenCV capture
cap = cv2.VideoCapture(1)  # Use 0 for the built-in webcam

# Initialize video buffer
video_buffer = [[None] * VIDEO_BUFFER_SIZE,0]

# Flag to indicate recording state
recording = False

fps = 30
frame_time = 1/fps

cam = activate_camera()

def capture_frames():
    global recording, video_buffer

    while True:
        start_time = time.time()
        frame = cam.capture_array()
        frame_cap_time = time.time() - start_time
        frame_ratio = f'{frame_cap_time/frame_time*100}%'
        next_frame_index = (video_buffer[1] + 1) % VIDEO_BUFFER_SIZE
        print(next_frame_index,frame_ratio)
        video_buffer[0][next_frame_index] = frame
        video_buffer[1] = next_frame_index
        # Delay to control the frame rate of the video capture
        current_time = time.time()
        sleep_time = current_time%frame_time
        time.sleep(sleep_time)  # Approximately 30 fps (1/30 = 0.033 seconds per frame)
        if cv2.waitKey(1) == ord(' '):
            save_video()
            break
        
video_num = 0
def save_video():
    global video_buffer, video_num
    cam.stop()
    # Perform a deep copy
    video_buffer_copy = copy.deepcopy(video_buffer)
    frame_index = video_buffer_copy[1]
    video_array = video_buffer[0]
  
    ordered_video_array = video_array[frame_index:] + video_array[:frame_index]
    filtered_video_array =  [x for x in ordered_video_array if x is not None]  
    frame_size = (filtered_video_array[0].shape[1], filtered_video_array[0].shape[0])  
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Choose codec (codec list: https://www.fourcc.org/codecs.php)
    video_name = f'ouput{video_num}.mp4'
    print(video_name)

    out = cv2.VideoWriter(video_name, fourcc, fps, frame_size)
    for index, frame in enumerate(filtered_video_array):
        out.write(frame)
        print(index)
        time.sleep(0.01)
    out.release()
    video_num+=1

if __name__ == '__main__':
    cv2.namedWindow('Press Space bar to start/stop recording')
    capture_frames()
