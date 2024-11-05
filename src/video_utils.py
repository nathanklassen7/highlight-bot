from subprocess import check_output
import time
from picamera2.encoders import H264Encoder
from picamera2.outputs import CircularOutput
from picamera2 import Picamera2

BUFFER_FILE_NAME = "buffer.h264"
fps = 60
dur = 20

picam2 = Picamera2()
vconfig = picam2.create_video_configuration(controls={"FrameRate": fps})
picam2.configure(vconfig)

output = CircularOutput(file=BUFFER_FILE_NAME,buffersize=int(fps * (dur+1)),outputtofile=False)
encoder = H264Encoder(10000000)

def start_camera():
    picam2.start()

def stop_camera():
    picam2.stop()

def start_recording_video():
    picam2.start_encoder(encoder, output)

def stop_recording_video():
    picam2.stop_encoder()

def capture_video_data():
    video_end_time = time.time()
    picam2.stop_encoder()
    video_duration = float(check_output(['ffprobe', '-i', BUFFER_FILE_NAME, "-count_packets", '-show_entries', 'stream=nb_read_packets', '-v', 'quiet', '-of', 'csv=p=0']).decode('utf-8').strip()) / fps
    video_start_time = video_end_time - video_duration
    return video_start_time