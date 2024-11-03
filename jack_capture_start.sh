#!/bin/bash

set -x
date

# start the jack server
export JACK_NO_AUDIO_RESERVATION=1
echo "Starting JACK server"
#/usr/local/bin/jackd -R -dalsa -dhw:0 -r48000 -p1024 -n3 &
/bin/jackd -R -dalsa -dhw:3,0 -r48000 -p1024 -n3 &

# run timemachine in tmux, since it waits for input
sleep 5
echo "Starting Timemachine"
tmux new-session -d '/bin/jack_capture -O 7777 --format wav --filename-prefix /home/nathanklassen/highlight-bot/audio/ --port system:capture_1 --port system:capture_2 --timemachine --timemachine-prebuffer 20 -Hc /home/nathanklassen/highlight-bot/jack_finish.sh'
