from audio_utils import capture_audio_data, start_recording_audio, stop_recording_audio,  timestamp_file
from consts import CLIP_DIRECTORY
from subprocess import call
import threading 
import time
import os

from encoding_utils import encode_video
from output import cleanup, indicate_recording_start, indicate_recording_stop, indicate_saved_video, indicate_writing, wait_for_press, wait_for_release, write_led, indicate_save_error
from server import init_server
from video_utils import capture_video_data, start_camera, stop_camera, start_recording_video, stop_recording_video

def main():
    time.sleep(1)
    threading.Thread(target=init_server, daemon=True).start()
    call([f'mkdir -p {CLIP_DIRECTORY}'],shell=True)

    if os.path.exists(timestamp_file):
        os.remove(timestamp_file)
    try:
        write_led('on', True)
        while True:
            time.sleep(1)
        while True:
            start_camera()
            indicate_recording_start()
            while True:
                start_recording_video()
                start_recording_audio()
                
                wait_for_press(True)
                write_led('record',False)
                signal = wait_for_release(True)
                
                if signal == 'long':
                    stop_recording_video()
                    stop_recording_audio()
                    break
                
                indicate_writing()
                
                video_start_time = capture_video_data()
                
                audio_start_time = capture_audio_data()
                
                if audio_start_time == 0:
                    print("Error capturing audio")
                    indicate_save_error()
                    continue
                
                encode_result = encode_video(audio_start_time, video_start_time)
                
                if encode_result == 1:
                    print("Error converting .h264 file and joining audio")
                    indicate_save_error()
                else:
                    print("Converted!")
                    indicate_saved_video()
                
            indicate_recording_stop()
            stop_camera()
            wait_for_release()
            wait_for_press(False)
            wait_for_release()
    finally:
        cleanup()

if __name__ == '__main__':
    main()