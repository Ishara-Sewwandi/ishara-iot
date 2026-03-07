#!/bin/bash
# Start LiveKit Fish Detection Publisher
# Streams camera feed with real-time YOLOv8 fish detection to LiveKit

cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Load environment variables if .env exists
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
fi

echo "=========================================="
echo "🐟 Fish Detection LiveKit Publisher"
echo "=========================================="
echo "LiveKit URL:  ${LIVEKIT_URL}"
echo "Room:         ${LIVEKIT_ROOM}"
echo "Identity:     ${LIVEKIT_IDENTITY}"
echo "=========================================="

# Start the publisher with fish detection
python3 livekit_publisher.py --width 640 --height 480 --fps 15
