#!/bin/bash

# Startup script for Fish Mortality Detection System
# This script activates the virtual environment and runs the main application

cd /home/koi/Documents/GitHub/ishara-iot

# Activate virtual environment with system-site-packages access
export PYTHONPATH=/usr/lib/python3/dist-packages:$PYTHONPATH
source venv/bin/activate

echo "Starting Fish Mortality Detection System..."
echo "Press Ctrl+C to stop"
echo ""

python3 main.py
