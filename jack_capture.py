import time

from pythonosc.osc_message_builder import OscMessageBuilder
from pythonosc.udp_client import UDPClient
import RPi.GPIO as GPIO

import os

HOST = '127.0.0.1'
PORT = 7777

START = OscMessageBuilder('/jack_capture/tm/start').build()
STOP = OscMessageBuilder('/jack_capture/tm/stop').build()
client = UDPClient(HOST, PORT)

if __name__ == '__main__':
    client.send(START)
    client.send(STOP)
    # time.sleep(0.1)
    # audio_dir = 'audio/'
    # audio_files = sorted(os.listdir(audio_dir))
    # if audio_files:
    #     first_file = audio_files[0]
    #     src = os.path.join(audio_dir, first_file)
    #     dst = 'output.wav'
    #     os.system(f'mv -f {src} {dst}')