from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import CircularOutput
from consts import CLIP_DIRECTORY
from subprocess import call, DEVNULL
from datetime import datetime
import threading 
import time

from output import cleanup, indicate_recording_start, indicate_recording_stop, indicate_saved_video, indicate_writing, wait_for_press, wait_for_release, write_led, indicate_save_error
from server import init_server

BUFFER_FILE_NAME = 'buffer.h264'

def main(): 
    threading.Thread(target=init_server, daemon=True).start()
    call([f'mkdir -p {CLIP_DIRECTORY}'],shell=True)
    picam2 = Picamera2()
    fps = 60
    dur = 20
    vconfig = picam2.create_video_configuration(controls={"FrameRate": fps})
    picam2.configure(vconfig)
    encoder = H264Encoder(10000000)
    n = 0
    
    try:
        write_led('on', True)
        while True:
            picam2.start()
            indicate_recording_start()
            while True:
                output = CircularOutput(file=BUFFER_FILE_NAME,buffersize=int(fps * (dur+1)),outputtofile=False)
                picam2.start_encoder(encoder, output)
                wait_for_press(True)
                write_led('record',False)
                signal = wait_for_release(True)
                if signal == 'long':
                    picam2.stop_encoder()
                    break
                indicate_writing()
                picam2.stop_encoder()
                timestamp = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
                mp4_file_name = f'clips/{timestamp}.mp4'
                if call([f"ffmpeg -r {fps} -i {BUFFER_FILE_NAME} -c copy {mp4_file_name} -y"], shell=True,stdout=DEVNULL, stderr=DEVNULL) == 1:
                    print("Error converting .h264 file")
                    indicate_save_error()
                else:
                    print("Converted!")
                    call([f"rm {BUFFER_FILE_NAME}"],shell=True)
                    indicate_saved_video()
                n = n + 1
            indicate_recording_stop()
            picam2.stop()
            wait_for_release()
            wait_for_press(False)
            wait_for_release()
    finally:
        cleanup()

if __name__ == '__main__':
    main()