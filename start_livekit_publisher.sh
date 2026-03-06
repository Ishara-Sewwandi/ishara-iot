#!/bin/bash
# Start LiveKit Fish Detection Publisher

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

# Start the publisher
python3 livekit_publisher.py --width 640 --height 480 --fps 15
