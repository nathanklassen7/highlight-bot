#!/usr/bin/python3
import time

import numpy as np

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import CircularOutput

lsize = (320, 240)
picam2 = Picamera2()
video_config = picam2.create_video_configuration({"size": (1280, 720), "format": "RGB888"})
picam2.configure(video_config)
picam2.start_preview()
encoder = H264Encoder(1000000, repeat=True)
encoder.output = CircularOutput()
picam2.start()
picam2.start_encoder(encoder)

w, h = lsize
prev = None
encoding = False
ltime = 0
startTime= time.time()
while True:
    elapsedTime = time.time()-startTime
    if elapsedTime > 5:
        if not encoding:
            epoch = int(time.time())
            encoder.output.fileoutput = f"{epoch}.h264"
            encoder.output.start()
            encoding = True
            print('encoding')
        ltime = time.time()
    else:
        if encoding and time.time() - ltime > 5.0:
            encoder.output.stop()
            encoding = False