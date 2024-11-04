#!/bin/bash

set -x
date

# start the jack server
export JACK_NO_AUDIO_RESERVATION=1
echo "Starting JACK server"
#/usr/local/bin/jackd -R -dalsa -dhw:0 -r48000 -p1024 -n3 &
/bin/jackd -R -dalsa -dhw:3,0 -r48000 -p1024 -n3 &