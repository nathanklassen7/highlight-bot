#!/bin/bash
SESSION="highlight-bot"

tmux kill-session -t "$SESSION" 2>/dev/null

pkill -f jack_capture 2>/dev/null
pkill -f jackd 2>/dev/null
pkill -f ngrok 2>/dev/null

echo "highlight-bot stopped"
