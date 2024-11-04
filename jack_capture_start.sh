#!/bin/bash
echo "Starting Timemachine"
tmux new-session -d '/bin/jack_capture -O 7777 --format wav --filename-prefix /home/nathanklassen/highlight-bot/audio/ --port system:capture_1 --port system:capture_2 --timemachine --timemachine-prebuffer 20 -Hc /home/nathanklassen/highlight-bot/jack_finish.sh'
