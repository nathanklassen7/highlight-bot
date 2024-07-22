import time

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import CircularOutput

picam2 = Picamera2()
fps = 60
dur = 10
micro = int((1 / fps) * 1000000)
vconfig = picam2.create_video_configuration({"size": (1536, 864)})
picam2.configure(vconfig)
encoder = H264Encoder()
output = CircularOutput(buffersize=int(fps * (dur + 0.2)))
output.fileoutput = "file.h264"
picam2.start_recording(encoder, output)
time.sleep(dur)
output.stop()