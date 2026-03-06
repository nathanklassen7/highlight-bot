#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
tmux new-session -d "/bin/jack_capture -O 7777 --port system:capture_1 --port system:capture_2 --timemachine --timemachine-prebuffer 20 -Hc ${SCRIPT_DIR}/jack_finish.sh ${SCRIPT_DIR}/buffer.wav"
