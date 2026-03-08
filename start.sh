#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
set -a
source "$SCRIPT_DIR/.env"
set +a
SESSION="highlight-bot"

HOTSPOT_SSID="${HOTSPOT_SSID:-HighlightBot}"
HOTSPOT_PASSWORD="${HOTSPOT_PASSWORD:-highlights}"

# Poll for internet connectivity (20 seconds)
TRAVEL_MODE=0
echo "Checking for internet connection..."
for i in $(seq 1 10); do
    if ping -c 1 -W 1 8.8.8.8 >/dev/null 2>&1; then
        echo "Internet connection found."
        break
    fi
    echo "  No connection (attempt $i/10)..."
    sleep 2
    if [ "$i" -eq 10 ]; then
        echo "No internet after 20 seconds. Starting in travel mode."
        TRAVEL_MODE=1
    fi
done

# Kill existing session if present
tmux kill-session -t "$SESSION" 2>/dev/null

if [ "$TRAVEL_MODE" -eq 1 ]; then
    echo "Starting Wi-Fi hotspot ($HOTSPOT_SSID)..."
    sudo nmcli device wifi hotspot ifname wlan0 ssid "$HOTSPOT_SSID" password "$HOTSPOT_PASSWORD"

    # Window 0: JACK server
    tmux new-session -d -s "$SESSION" -n jack
    tmux send-keys -t "$SESSION:jack" "cd $SCRIPT_DIR && bash jack_server_start.sh" Enter

    sleep 2

    # Window 1: main app (travel mode — no Slack server)
    tmux new-window -t "$SESSION" -n app
    tmux send-keys -t "$SESSION:app" "cd $SCRIPT_DIR && source env/bin/activate && TRAVEL_MODE=1 python3 src/main.py" Enter
else
    # Window 0: JACK server
    tmux new-session -d -s "$SESSION" -n jack
    tmux send-keys -t "$SESSION:jack" "cd $SCRIPT_DIR && bash jack_server_start.sh" Enter

    sleep 2

    # Window 1: main app (normal mode — Slack + web server)
    tmux new-window -t "$SESSION" -n app
    tmux send-keys -t "$SESSION:app" "cd $SCRIPT_DIR && source env/bin/activate && python3 src/main.py" Enter
fi
