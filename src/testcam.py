from picamera2 import Picamera2
import time
from picamera2.encoders import H264Encoder, Quality
from subprocess import call

picam2 = Picamera2()

camera_config = picam2.create_video_configuration(controls={"FrameRate": 60},main={"size":(1536,864)})
picam2.configure(camera_config)
encoder = H264Encoder()
picam2.start_recording(encoder, 'test.h264', quality=Quality.HIGH)
time.sleep(5)
picam2.stop_recording()
call([f"ffmpeg -r {60} -i test.h264 -c copy test.mp4 -y"], shell=True)
call([f"rm test.h264"],shell=True)