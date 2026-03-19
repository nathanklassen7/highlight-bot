import json
import shutil
from subprocess import check_output, CalledProcessError
import os
import time

from pythonosc.osc_message_builder import OscMessageBuilder
from pythonosc.udp_client import UDPClient

if not os.path.exists("audio_config.json"):
    shutil.copy("default_audio_config.json", "audio_config.json")

with open("audio_config.json") as _f:
    _cfg = json.load(_f)

timestamp_file = "time.tme"
AUDIO_BUFFER_FILE = 'buffer.wav'
TIMESTAMP_TIMEOUT = 2.0

HOST = _cfg["osc_host"]
PORT = _cfg["osc_port"]

START = OscMessageBuilder('/jack_capture/tm/start').build()
STOP = OscMessageBuilder('/jack_capture/stop').build()
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = UDPClient(HOST, PORT)
    return _client


def get_timestamp():
    if not os.path.exists(timestamp_file):
        return 0
    with open(timestamp_file, 'r') as f:
        line = f.readline()
        return float(line)


def _kill_existing_jack_capture():
    try:
        check_output(['pkill', '-f', 'jack_capture'])
        time.sleep(0.5)
    except CalledProcessError:
        pass


def start_recording_audio():
    _kill_existing_jack_capture()

    if os.path.exists(timestamp_file):
        os.remove(timestamp_file)
    if os.path.exists(AUDIO_BUFFER_FILE):
        os.remove(AUDIO_BUFFER_FILE)

    check_output(['sh', 'jack_capture_start.sh'])


def stop_recording_audio():
    _get_client().send(STOP)


def _wait_for_timestamp(timeout=TIMESTAMP_TIMEOUT, poll=0.1):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if os.path.exists(timestamp_file):
            return True
        time.sleep(poll)
    return False


def capture_audio_data():
    _get_client().send(START)
    _get_client().send(STOP)

    if not _wait_for_timestamp():
        print("Timed out waiting for jack_capture to finish writing")
        return 0

    try:
        duration_str = check_output([
            'ffprobe', '-i', AUDIO_BUFFER_FILE,
            '-show_entries', 'format=duration',
            '-v', 'quiet', '-of', 'csv=p=0',
        ]).decode('utf-8').strip()
        if not duration_str or duration_str == 'N/A':
            print("Audio buffer not ready yet (duration N/A)")
            return 0
        audio_duration = float(duration_str)
        audio_end_time = get_timestamp()
        audio_start_time = audio_end_time - audio_duration
        return audio_start_time
    except (CalledProcessError, FileNotFoundError) as e:
        print(f"Error capturing audio data: {e}")
        return 0
    except (ValueError, OSError) as e:
        print(f"Error parsing audio metadata: {e}")
        return 0
