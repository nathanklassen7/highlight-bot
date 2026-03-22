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
    python3-pip python3-venv python3-dev \
    python3-picamera2 python3-numpy python3-opencv python3-scipy python3-gpiozero \
    jackd2 libjack-jackd2-dev liblo-dev \
    tmux ffmpeg libcamera-apps
```

### 2. Build jack_capture from source

The apt version of `jack_capture` is compiled without OSC support. Build from source with `liblo`:

```bash
git clone https://github.com/kmatheussen/jack_capture.git /tmp/jack_capture
cd /tmp/jack_capture
make
sudo make install
```

### 3. Clone and install

```bash
git clone <repo-url> ~/highlight-bot
cd ~/highlight-bot
python3 -m venv --system-site-packages env
source env/bin/activate
pip install -r requirements.txt
```

### 4. Configure Slack App

The bot uses **Slack Socket Mode**, which connects outbound over WebSocket — no public URL, ngrok, or port forwarding required.

In your [Slack App settings](https://api.slack.com/apps):

1. Go to **Socket Mode** and enable it.
2. Go to **Basic Information → App-Level Tokens**, create a token with the `connections:write` scope. Copy the `xapp-...` token.
3. Ensure your bot has the necessary **Bot Token Scopes** (under OAuth & Permissions): `app_mentions:read`, `chat:write`, `commands`, `files:write`.
4. Ensure **Event Subscriptions** are enabled and `app_mention` is subscribed.
5. Ensure your `/hl` **Slash Command** is registered.

### 5. Configure environment

Create a `.env` file in the project root:

```bash
SLACK_BOT_TOKEN="xoxb-your-bot-token"
SLACK_APP_TOKEN="xapp-your-app-level-token"
# DISABLE_SLACK=1  # Set to 1 to disable the Slack server
```

Pin the USB audio device to a stable card index at 3 so it doesn't shift between boots:

```bash
echo 'options snd_usb_audio index=3' | sudo tee /etc/modprobe.d/alsa-base.conf
```

Both `camera_config.json` and `audio_config.json` are created automatically from their defaults on first run. To customize them beforehand:

```bash
cp default_camera_config.json camera_config.json
cp default_audio_config.json audio_config.json
```

### 6. Set up auto-start

Install the systemd user service:

```bash
mkdir -p ~/.config/systemd/user

cat > ~/.config/systemd/user/highlight-bot.service << 'EOF'
[Unit]
Description=Highlight Bot
After=network-online.target sound.target
Wants=network-online.target

[Service]
Type=forking
ExecStart=%h/highlight-bot/start.sh
ExecStop=%h/highlight-bot/stop.sh
RemainAfterExit=yes
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

loginctl enable-linger $USER
systemctl --user daemon-reload
systemctl --user enable highlight-bot.service
```

### 7. (Optional) Disable the desktop

Free up ~400MB of RAM by booting to CLI:

```bash
sudo raspi-config nonint do_boot_behaviour B1
```

### 8. Reboot

```bash
sudo reboot
```

The bot will start automatically on boot.

## Managing the bot

| Action                | Command                                  |
| --------------------- | ---------------------------------------- |
| View processes        | `tmux attach -t highlight-bot`           |
| Switch windows        | `Ctrl-B 0` (jack), `Ctrl-B 1` (app)      |
| Detach (keep running) | `Ctrl-B d`                               |
| Stop                  | `systemctl --user stop highlight-bot`    |
| Start                 | `systemctl --user start highlight-bot`   |
| Restart               | `systemctl --user restart highlight-bot` |
| Status                | `systemctl --user status highlight-bot`  |
| Logs                  | `journalctl --user -u highlight-bot -f`  |

## Guide

On the actual bot, the flashing red light indicates that it's recording. The green light should always be on — if it's not, there's an issue with the script.
When the light is flashing, the bot is always recording and pushing the red button will save the PAST 20 seconds of footage.
When you're done, hold the clip button down until the red light flashes fast a bunch of times. It should then be off (green light on but no flashing red light).
To wake it up, just press the clip button. It should start flashing red again.

## Slack commands

| Command                     | Description                          |
| --------------------------- | ------------------------------------ |
| `/hl`                       | List saved clips (ephemeral)         |
| `/hl public`                | List saved clips (posted to channel) |
| `/hl start` or `/hl record` | Start recording                      |
| `/hl stop`                  | Stop recording                       |
| `/hl clip`                  | Save the last 20s as a clip          |
| `/hl pic`                   | Capture a frame and post to channel  |
| `/hl status`                | Show current state                   |
| `/hl config`                | Show camera config                   |
| `/hl config <key> <value>`  | Update a config value (while idle)   |
| `/hl timeout`               | Show inactivity timeout              |
| `/hl timeout <hours>`       | Set inactivity timeout               |

You can also @mention the bot with `start`, `stop`, `clip`, or `status`.

## Optimizing Pi Memory Headroom

### Disabling Audio Servers for JACK (Headless Raspberry Pi)

When using JACK for audio recording, PulseAudio and PipeWire can be disabled.

Disable and mask all conflicting audio services:

```bash
systemctl --user disable --now pulseaudio pulseaudio.socket pipewire pipewire-pulse wireplumber
systemctl --user mask pulseaudio pulseaudio.socket pipewire pipewire-pulse wireplumber
```

### Reduce GPU memory

Add to `/boot/firmware/config.txt`:

```ini
gpu_mem=16
```
