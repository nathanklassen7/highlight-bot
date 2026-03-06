from subprocess import check_output, CalledProcessError
import os

from pythonosc.osc_message_builder import OscMessageBuilder
from pythonosc.udp_client import UDPClient

timestamp_file = "time.tme"
AUDIO_BUFFER_FILE = 'buffer.wav'

HOST = '127.0.0.1'
PORT = 7777

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


def start_recording_audio():
    if os.path.exists(timestamp_file):
        os.remove(timestamp_file)
    if os.path.exists(AUDIO_BUFFER_FILE):
        os.remove(AUDIO_BUFFER_FILE)

    check_output(['sh', 'jack_capture_start.sh'])


def stop_recording_audio():
    _get_client().send(STOP)


def capture_audio_data():
    _get_client().send(START)
    _get_client().send(STOP)

    try:
        duration_str = check_output([
            'ffprobe', '-i', AUDIO_BUFFER_FILE,
            '-show_entries', 'format=duration',
            '-v', 'quiet', '-of', 'csv=p=0',
        ]).decode('utf-8').strip()
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
