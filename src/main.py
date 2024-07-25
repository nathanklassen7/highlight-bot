from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import CircularOutput
from consts import CLIP_DIRECTORY
from subprocess import call, DEVNULL
from datetime import datetime
import threading 

from server import init_server

BUFFER_FILE_NAME = 'buffer.h264'


if __name__ == '__main__':
    threading.Thread(target=init_server, daemon=True).start()
    call([f'mkdir -p {CLIP_DIRECTORY}'],shell=True)
    picam2 = Picamera2()
    fps = 60
    dur = 3
    vconfig = picam2.create_video_configuration(controls={"FrameRate": fps})
    picam2.configure(vconfig)
    encoder = H264Encoder(20000000)
    n = 0
    picam2.start()
    while True:
        output = CircularOutput(file=BUFFER_FILE_NAME,buffersize=int(fps * (dur+1)),outputtofile=False)
        picam2.start_encoder(encoder, output)
        if input("Press enter to save or q+enter to quit") == 'q':
            picam2.stop_recording()
            break
        picam2.stop_encoder()
        timestamp = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        mp4_file_name = f'clips/{timestamp}.mp4'
        if call([f"ffmpeg -r {fps} -i {BUFFER_FILE_NAME} -c copy {mp4_file_name} -y"], shell=True,stdout=DEVNULL, stderr=DEVNULL) == 1:
            print("Error converting .h264 file")
        else:
            print("Converted!")
            call([f"rm {BUFFER_FILE_NAME}"],shell=True)
        n = n + 1