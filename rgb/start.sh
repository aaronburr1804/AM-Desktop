#!/usr/bin/env bash
# Server start script for Mechanicus RGB, place in ~/.local/share/mechanicus-rgb/start.sh
pgrep -x openrgb > /dev/null || QT_QPA_PLATFORM=offscreen setsid -f /usr/bin/openrgb --server --noautoconnect
sleep 4
exec "$HOME/.local/share/mechanicus-rgb/venv/bin/python" "$HOME/.local/share/mechanicus-rgb/mechanicus_rgb.py" --pulse