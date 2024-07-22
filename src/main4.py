#!/usr/bin/python3
import time

import numpy as np

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import CircularOutput

picam2 = Picamera2()
video_config = picam2.create_video_configuration({"size": (1280, 720), "format": "RGB888"})
picam2.configure(video_config)
picam2.start_preview()
encoder = H264Encoder(1000000, repeat=True)
encoder.output = CircularOutput(buffersize=600, outputtofile=False)
picam2.start()
picam2.start_encoder(encoder)

prev = None
encoding = False
ltime = 0

time.sleep(5)
encoder.output.fileoutput = f"output.h264"
encoder.output.start()
time.sleep(5)
encoder.output.stop()
