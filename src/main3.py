from picamera2.encoders import H264Encoder
from picamera2.outputs import CircularOutput
from picamera2 import Picamera2
import time
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration())
encoder = H264Encoder()
output = CircularOutput()
picam2.start_recording(encoder, output)
# Now when it's time to start recording the output, including the previous 5 seconds:
output.fileoutput = "file.h264"
output.start()
time.sleep(10)
output.stop()