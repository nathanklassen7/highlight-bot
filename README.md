This code runs on a Raspberry Pi in the Faire office. It records video into a circular buffer, and when the Clip button is pressed it saves the **past** 20 seconds of footage.

To push updates, simply merge code to main and the Raspberry Pi will pull it when it is next rebooted.

## Setup on a new Raspberry Pi

### Prerequisites

- Raspberry Pi 4 (2GB+ RAM recommended)
- Raspberry Pi OS (headless / Lite recommended)
- Camera module connected via CSI
- USB audio interface
- SSH access

### 1. Install system dependencies

```bash
sudo apt update && sudo apt install -y \
    python3-pip python3-venv python3-picamera2 \
    jackd2 jack-capture tmux ffmpeg libcamera-apps
```

### 2. Install ngrok

Follow the instructions at https://ngrok.com/download to install ngrok and set up your auth token. Create `~/launch_ngrok.sh` with your ngrok command, e.g.:

```bash
#!/bin/bash
ngrok http --domain=your-domain.ngrok-free.app 3000
```

### 3. Clone and install

```bash
git clone <repo-url> ~/highlight-bot
cd ~/highlight-bot
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### 4. Configure

Copy the default configs:

```bash
cp default_camera_config.json camera_config.json
```

Create `audio_config.json`:

```json
{
    "osc_host": "127.0.0.1",
    "osc_port": 7777
}
```

Set your Slack bot token as an environment variable (add to `~/.bashrc`):

```bash
export SLACK_BOT_TOKEN="xoxb-your-token"
```

### 5. Set up auto-start

Install the systemd user service:

```bash
mkdir -p ~/.config/systemd/user

cat > ~/.config/systemd/user/highlight-bot.service << 'EOF'
[Unit]
Description=Highlight Bot (tmux session)
After=network-online.target sound.target
Wants=network-online.target

[Service]
Type=forking
ExecStart=/home/$USER/highlight-bot/start.sh
ExecStop=/home/$USER/highlight-bot/stop.sh
RemainAfterExit=yes

[Install]
WantedBy=default.target
EOF

loginctl enable-linger $USER
systemctl --user daemon-reload
systemctl --user enable highlight-bot.service
```

### 6. (Optional) Disable the desktop

Free up ~400MB of RAM by booting to CLI:

```bash
sudo raspi-config nonint do_boot_behaviour B1
```

### 7. Reboot

```bash
sudo reboot
```

The bot will start automatically on boot.

## Managing the bot

| Action | Command |
|---|---|
| View processes | `tmux attach -t highlight-bot` |
| Switch windows | `Ctrl-B 0` (jack), `Ctrl-B 1` (ngrok), `Ctrl-B 2` (app) |
| Detach (keep running) | `Ctrl-B d` |
| Stop | `systemctl --user stop highlight-bot` |
| Start | `systemctl --user start highlight-bot` |
| Restart | `systemctl --user restart highlight-bot` |
| Status | `systemctl --user status highlight-bot` |

## Guide

On the actual bot, the flashing red light indicates that it's recording. The green light should always be on — if it's not, there's an issue with the script.
When the light is flashing, the bot is always recording and pushing the red button will save the PAST 20 seconds of footage.
When you're done, hold the clip button down until the red light flashes fast a bunch of times. It should then be off (green light on but no flashing red light).
To wake it up, just press the clip button. It should start flashing red again.

## Slack commands

| Command | Description |
|---|---|
| `/hl` | List saved clips (ephemeral) |
| `/hl public` | List saved clips (posted to channel) |
| `/hl start` or `/hl record` | Start recording |
| `/hl stop` | Stop recording |
| `/hl clip` | Save the last 20s as a clip |
| `/hl pic` | Capture a frame and post to channel |
| `/hl status` | Show current state |
| `/hl config` | Show camera config |
| `/hl config <key> <value>` | Update a config value (while idle) |
| `/hl timeout` | Show inactivity timeout |
| `/hl timeout <hours>` | Set inactivity timeout |

You can also @mention the bot with `start`, `stop`, `clip`, or `status`.
