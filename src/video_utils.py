import os
from subprocess import check_output
import time
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import CircularOutput

VIDEO_BUFFER_FILE = "buffer.h264"
fps = 60
dur = 20

_picam2 = None
_encoder = None


def _get_camera():
    global _picam2, _encoder
    if _picam2 is None:
        _picam2 = Picamera2()
        vconfig = _picam2.create_video_configuration(controls={"FrameRate": fps})
        _picam2.configure(vconfig)
        _encoder = H264Encoder(10000000)
    return _picam2, _encoder


def start_camera():
    cam, _ = _get_camera()
    cam.start()


def stop_camera():
    cam, _ = _get_camera()
    cam.stop()


def start_recording_video():
    cam, encoder = _get_camera()
    if os.path.exists(VIDEO_BUFFER_FILE):
        os.remove(VIDEO_BUFFER_FILE)
    output = CircularOutput(
        file=VIDEO_BUFFER_FILE,
        buffersize=int(fps * (dur + 1)),
        outputtofile=False,
    )
    cam.start_encoder(encoder, output)


def stop_recording_video():
    cam, _ = _get_camera()
    cam.stop_encoder()


SNAPSHOT_FILE = "snapshot.jpg"


def capture_frame():
    cam, _ = _get_camera()
    was_stopped = not cam.started
    if was_stopped:
        cam.start()
    cam.capture_file(SNAPSHOT_FILE)
    if was_stopped:
        cam.stop()
    return SNAPSHOT_FILE


def capture_video_data():
    cam, _ = _get_camera()
    video_end_time = time.time()
    cam.stop_encoder()
    packet_count = check_output([
        'ffprobe', '-i', VIDEO_BUFFER_FILE,
        '-count_packets',
        '-show_entries', 'stream=nb_read_packets',
        '-v', 'quiet', '-of', 'csv=p=0',
    ]).decode('utf-8').strip()
    video_duration = float(packet_count) / fps
    video_start_time = video_end_time - video_duration
    return video_start_time
