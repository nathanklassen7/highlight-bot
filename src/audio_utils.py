from subprocess import check_output
import time
import os

from pythonosc.osc_message_builder import OscMessageBuilder
from pythonosc.udp_client import UDPClient

timestamp_file = "time.tme"

HOST = '127.0.0.1'
PORT = 7777

START = OscMessageBuilder('/jack_capture/tm/start').build()
STOP = OscMessageBuilder('/jack_capture/tm/stop').build()
client = UDPClient(HOST, PORT)

def get_timestamp():
    if not os.path.exists(timestamp_file):
        return 0
    with open(timestamp_file, 'r') as f:
        line = f.readline()
        return float(line)

        
def delete_timestamp():
    if os.path.exists(timestamp_file):
        os.remove(timestamp_file)
        
def wait_and_delete_timestamp():
    while not os.path.exists(timestamp_file):
        time.sleep(0.1)
    os.remove(timestamp_file)
    
def remove_old_audio_files(files):
    most_recent_file = None
    if len(files) != 1:
        most_recent_file = max(files, key=lambda f: os.path.getctime(os.path.join('audio', f)))
    else:
        most_recent_file = files[0]
    for f in files:
        if f != most_recent_file:
            os.remove(os.path.join('audio', f))
        
def get_audio_data():
    if os.path.exists(timestamp_file):
        os.remove(timestamp_file)
    files = os.listdir('audio')
    if len(files) != 1:
        remove_old_audio_files(files)
    wav_src = f'audio/{files[0]}'
    client.send(START)
    client.send(STOP)
    audio_duration = float(check_output(['ffprobe', '-i', wav_src, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=p=0']).decode('utf-8').strip())
    audio_end_time = get_timestamp()
    audio_start_time = audio_end_time - audio_duration

    return wav_src, audio_start_time