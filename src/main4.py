#!/usr/bin/python3
import time

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import CircularOutput

picam2 = Picamera2()
fps = 30
dur = 5
vconfig = picam2.create_video_configuration(controls={"FrameRate": fps})
picam2.configure(vconfig)
encoder = H264Encoder(2000000, repeat=True)
output = CircularOutput(buffersize=int(fps * (dur + 1)), outputtofile=True)
output.fileoutput = "file.h264"
picam2.start_recording(encoder, output)
time.sleep(5)
output.start()
print('test')
time.sleep(dur)
output.stop()