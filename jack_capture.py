import time

from pythonosc.osc_message_builder import OscMessageBuilder
from pythonosc.udp_client import UDPClient
import RPi.GPIO as GPIO

import os

from src.audio_utils import get_audio_data

HOST = '127.0.0.1'
PORT = 7777

START = OscMessageBuilder('/jack_capture/tm/start').build()
STOP = OscMessageBuilder('/jack_capture/tm/stop').build()
client = UDPClient(HOST, PORT)

if __name__ == '__main__':
    wav_src, audio_start_time = get_audio_data()
    time.sleep(0.1)
    os.remove(wav_src)
    print(audio_start_time)
    # audio_dir = 'audio/'
    # audio_files = sorted(os.listdir(audio_dir))
    # if audio_files:
    #     first_file = audio_files[0]
    #     src = os.path.join(audio_dir, first_file)
    #     dst = 'output.wav'
    #     os.system(f'mv -f {src} {dst}')