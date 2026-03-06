#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
date +%s.%N > "${SCRIPT_DIR}/time.tme"
