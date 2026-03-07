#!/bin/bash
# Start script for Flask camera server + LiveKit bridge
# Used by systemd service

cd /home/koi/Documents/GitHub/ishara-iot
source venv/bin/activate

# Load environment variables
set -a
source .env
set +a

echo "Starting Flask camera server..."
python3 realtime_streaming_server.py
