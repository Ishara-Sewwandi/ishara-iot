#!/bin/bash
# API Server Startup Script
# This script runs the API server with proper environment setup
# It uses system Python for Picamera2 support while accessing venv packages

cd /home/koi/Documents/GitHub/ishara-iot

# Load environment variables (LiveKit credentials, etc.)
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
fi

# Add venv site-packages to PYTHONPATH so system Python can find Flask
export PYTHONPATH="/home/koi/Documents/GitHub/ishara-iot/venv/lib/python3.13/site-packages:$PYTHONPATH"

echo "=========================================="
echo "🐟 Fish Monitoring API Server"
echo "=========================================="
echo "LiveKit URL:  ${LIVEKIT_URL}"
echo "Room:         ${LIVEKIT_ROOM}"
echo "API:          http://0.0.0.0:5000"
echo "Token:        http://0.0.0.0:5000/api/livekit/token"
echo "=========================================="

# Run with system Python (has libcamera access)
python3 api_server.py
