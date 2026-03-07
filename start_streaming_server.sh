#!/bin/bash

# Real-Time Streaming Server Startup Script
# Runs both detection models and streams to Spring Boot frontend

cd /home/koi/Documents/GitHub/ishara-iot

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Real-Time Streaming Server${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Features:${NC}"
echo "  ✓ Fish Detection (YOLOv8)"
echo "  ✓ Health Detection (6 classes)"
echo "  ✓ Live video streaming"
echo "  ✓ Real-time WebSocket updates"
echo "  ✓ Spring Boot integration"
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✓${NC} Virtual environment activated"
else
    echo -e "${YELLOW}⚠${NC} Virtual environment not found"
    echo "Creating virtual environment..."
    python3 -m venv venv --system-site-packages
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Check if required packages are installed
echo ""
echo "Checking dependencies..."

python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing Flask..."
    pip install flask flask-cors flask-socketio
fi

python3 -c "import cv2" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing OpenCV..."
    pip install opencv-python
fi

python3 -c "import ultralytics" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing Ultralytics..."
    pip install ultralytics
fi

echo -e "${GREEN}✓${NC} All dependencies ready"
echo ""

# Get local IP address
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Server Information${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Local IP:${NC} $LOCAL_IP"
echo ""
echo -e "${BLUE}Access Points:${NC}"
echo "  • API Info:        http://$LOCAL_IP:5000"
echo "  • Video Stream:    http://$LOCAL_IP:5000/video/stream"
echo "  • Detection API:   http://$LOCAL_IP:5000/api/detections"
echo "  • WebSocket:       ws://$LOCAL_IP:5000"
echo ""
echo -e "${BLUE}Spring Boot Integration:${NC}"
echo "  Configure your frontend to connect to:"
echo "  • REST API: http://$LOCAL_IP:5000/api/detections"
echo "  • WebSocket: ws://$LOCAL_IP:5000"
echo ""
echo -e "${BLUE}Controls:${NC}"
echo "  • Press Ctrl+C to stop server"
echo ""
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Starting server..."
echo ""

echo "Local WebSocket/MJPEG streaming is deprecated."
echo "This installation now uses LiveKit only."
echo "To run the LiveKit publisher, use: ./start_livekit_publisher.sh"
exit 0
