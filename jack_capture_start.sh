#!/bin/bash
tmux new-session -d '/bin/jack_capture -O 7777 --port system:capture_1 --port system:capture_2 --timemachine --timemachine-prebuffer 20 -Hc /home/nathanklassen/highlight-bot/jack_finish.sh /home/nathanklassen/highlight-bot/buffer.wav'
