from subprocess import call, check_output
import os
import time

from pythonosc.osc_message_builder import OscMessageBuilder
from pythonosc.udp_client import UDPClient

timestamp_file = "time.tme"
AUDIO_BUFFER_FILE = 'buffer.wav'

HOST = '127.0.0.1'
PORT = 7777

START = OscMessageBuilder('/jack_capture/tm/start').build()
STOP = OscMessageBuilder('/jack_capture/stop').build()
client = UDPClient(HOST, PORT)

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

    call(['sh jack_capture_start.sh'], shell=True)
    
def stop_recording_audio():
    client.send(STOP)

def capture_audio_data():
    
    client.send(START)
    client.send(STOP)
    
    try:
        audio_duration = float(check_output(['ffprobe', '-i', AUDIO_BUFFER_FILE, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=p=0']).decode('utf-8').strip())
        audio_end_time = get_timestamp()
        audio_start_time = audio_end_time - audio_duration

        return audio_start_time
    except:
        return 0
