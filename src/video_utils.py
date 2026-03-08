import json
import os
from subprocess import check_output
import time
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import CircularOutput
from PIL import Image

VIDEO_BUFFER_FILE = "buffer.h264"

_picam2 = None
_encoder = None
_cfg = None

def _load_config():
    global _cfg
    with open("camera_config.json") as f:
        _cfg = json.load(f)
    return _cfg


def _get_camera():
    global _picam2, _encoder
    if _cfg is None:
        _load_config()
    if _picam2 is None:
        _picam2 = Picamera2()
        main_size = None
        if "width" in _cfg and "height" in _cfg:
            main_size = {"size": (_cfg["width"], _cfg["height"])}
        vconfig = _picam2.create_video_configuration(main=main_size, controls=_cfg.get("controls", {}))
        _picam2.configure(vconfig)
        _encoder = H264Encoder(_cfg["bitrate"])
    return _picam2, _encoder


def reinitialize_camera():
    global _picam2, _encoder
    if _picam2 is not None:
        if _picam2.started:
            try:
                _picam2.stop_encoder()
            except Exception:
                pass
            _picam2.stop()
        _picam2.close()
        _picam2 = None
        _encoder = None
    _load_config()
    _get_camera()


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
        buffersize=int(_cfg["fps"] * (_cfg["buffer_duration"] + 1)),
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
    frame = cam.capture_array("main")
    if was_stopped:
        cam.stop()
    Image.fromarray(frame).convert("RGB").save(SNAPSHOT_FILE)
    return SNAPSHOT_FILE


def capture_video_data():
    cam, _ = _get_camera()
    video_end_time = time.time()
    cam.stop_encoder()
    try:
        packet_count = check_output([
            'ffprobe', '-i', VIDEO_BUFFER_FILE,
            '-count_packets',
            '-show_entries', 'stream=nb_read_packets',
            '-v', 'quiet', '-of', 'csv=p=0',
        ]).decode('utf-8').strip()
        if not packet_count or packet_count == 'N/A':
            print("Video buffer not ready (packet count N/A)")
            return 0
        print(f"FPS: {_cfg['fps']}")
        video_duration = float(packet_count) / _cfg["fps"]
        video_start_time = video_end_time - video_duration
        return video_start_time
    except Exception as e:
        print(f"Error reading video metadata: {e}")
        return 0
