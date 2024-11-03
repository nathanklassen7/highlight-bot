from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import CircularOutput
from audio_utils import get_audio_data, get_timestamp, timestamp_file, wait_and_delete_timestamp
from consts import CLIP_DIRECTORY
from subprocess import call, DEVNULL, check_output
from datetime import datetime
import threading 
import time
import os
from pythonosc.osc_message_builder import OscMessageBuilder
from pythonosc.udp_client import UDPClient

from output import cleanup, indicate_recording_start, indicate_recording_stop, indicate_saved_video, indicate_writing, wait_for_press, wait_for_release, write_led, indicate_save_error
from server import init_server

HOST = '127.0.0.1'
PORT = 7777

START = OscMessageBuilder('/jack_capture/tm/start').build()
STOP = OscMessageBuilder('/jack_capture/tm/stop').build()
client = UDPClient(HOST, PORT)

BUFFER_FILE_NAME = 'buffer.h264'

compensation_ms = 0
video_duration_factor = 1

def main(): 
    threading.Thread(target=init_server, daemon=True).start()
    call([f'mkdir -p {CLIP_DIRECTORY}'],shell=True)
    picam2 = Picamera2()
    fps = 60
    dur = 20
    vconfig = picam2.create_video_configuration(controls={"FrameRate": fps})
    picam2.configure(vconfig)
    encoder = H264Encoder(10000000)
    n = 0
    if os.path.exists(timestamp_file):
        os.remove(timestamp_file)
    try:
        write_led('on', True)
        while True:
            picam2.start()
            indicate_recording_start()
            while True:
                output = CircularOutput(file=BUFFER_FILE_NAME,buffersize=int(fps * (dur+1)),outputtofile=False)
                picam2.start_encoder(encoder, output)
                [wav_src, audio_start_time] = get_audio_data()
                os.remove(wav_src)
                os.remove(timestamp_file)
                wait_for_press(True)
                write_led('record',False)
                signal = wait_for_release(True)
                if signal == 'long':
                    picam2.stop_encoder()
                    break
                indicate_writing()
                video_end_time = time.time()
                picam2.stop_encoder()
                video_duration = float(check_output(['ffprobe', '-i', BUFFER_FILE_NAME, "-count_packets", '-show_entries', 'stream=nb_read_packets', '-v', 'quiet', '-of', 'csv=p=0']).decode('utf-8').strip()) / fps * video_duration_factor
                video_start_time = video_end_time - video_duration
                [wav_src, audio_start_time] = get_audio_data()
                timestamp = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
                mp4_file_name = f'clips/{timestamp}.mp4'
                offset = int((audio_start_time - video_start_time)*1000 - compensation_ms)
                print(f'offset: {offset}')
                if(offset < 0):
                    offset = 0
                if call([f'ffmpeg -r {fps} -i {BUFFER_FILE_NAME} -i {wav_src} -c:v copy -af "adelay={offset}|{offset}" -c:a aac {mp4_file_name} -y -shortest'], shell=True,stdout=DEVNULL, stderr=DEVNULL) == 1:
                    print("Error converting .h264 file and joining audio")
                    indicate_save_error()
                else:
                    print("Converted!")
                    call([f"rm {BUFFER_FILE_NAME}"],shell=True)
                    indicate_saved_video()
                n = n + 1
                os.remove(timestamp_file)
                os.remove(wav_src)
            indicate_recording_stop()
            picam2.stop()
            wait_for_release()
            wait_for_press(False)
            wait_for_release()
    finally:
        cleanup()

if __name__ == '__main__':
    main()