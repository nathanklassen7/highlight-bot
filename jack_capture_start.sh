#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OSC_PORT=$(python3 -c "import json; print(json.load(open('${SCRIPT_DIR}/audio_config.json'))['osc_port'])")
PREBUFFER=$(python3 -c "import json; print(json.load(open('${SCRIPT_DIR}/camera_config.json'))['buffer_duration'])")
tmux new-session -d "/bin/jack_capture -O ${OSC_PORT} --port system:capture_1 --timemachine --timemachine-prebuffer ${PREBUFFER} -Hc ${SCRIPT_DIR}/jack_finish.sh ${SCRIPT_DIR}/buffer.wav"
