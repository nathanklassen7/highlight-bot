#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
set -a
source "$SCRIPT_DIR/.env"
set +a
SESSION="highlight-bot"

# Kill existing session if present
tmux kill-session -t "$SESSION" 2>/dev/null

# Window 0: JACK server
tmux new-session -d -s "$SESSION" -n jack
tmux send-keys -t "$SESSION:jack" "cd $SCRIPT_DIR && bash jack_server_start.sh" Enter

sleep 2

# Window 1: ngrok
tmux new-window -t "$SESSION" -n ngrok
tmux send-keys -t "$SESSION:ngrok" "bash ~/launch_ngrok.sh" Enter

# Window 2: main app
tmux new-window -t "$SESSION" -n app
tmux send-keys -t "$SESSION:app" "cd $SCRIPT_DIR && source env/bin/activate && python3 src/main.py" Enter
