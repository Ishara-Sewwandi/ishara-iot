#!/bin/bash
# API Server Startup Script
# This script runs the API server with proper environment setup
# It uses system Python for Picamera2 support while accessing venv packages

cd /home/koi/Documents/GitHub/ishara-iot

# Add venv site-packages to PYTHONPATH so system Python can find Flask
export PYTHONPATH="/home/koi/Documents/GitHub/ishara-iot/venv/lib/python3.13/site-packages:$PYTHONPATH"

# Run with system Python (has libcamera access)
python3 api_server.py
