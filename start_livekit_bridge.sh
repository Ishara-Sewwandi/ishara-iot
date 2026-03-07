#!/bin/bash
# Start script for LiveKit bridge
# Used by systemd service

cd /home/koi/Documents/GitHub/ishara-iot
source venv/bin/activate

# Load environment variables
set -a
source .env
set +a

# Wait for Flask server to be ready
echo "Waiting for Flask camera server on port 5000..."
for i in $(seq 1 30); do
    if curl -s http://192.168.8.101:5000 > /dev/null 2>&1; then
        echo "Flask server is ready!"
        break
    fi
    echo "  Attempt $i/30 - waiting..."
    sleep 2
done

echo "Starting LiveKit bridge..."
python3 livekit_bridge.py
