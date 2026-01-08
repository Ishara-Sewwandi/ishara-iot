#!/bin/bash
# Setup script to enable auto-start on boot for Fish Streaming Server

echo "=================================================="
echo "Fish Streaming Server - Auto-Start Setup"
echo "=================================================="
echo ""

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "Please run with sudo:"
    echo "sudo ./setup_autostart.sh"
    exit 1
fi

# Get the actual user (not root)
ACTUAL_USER=${SUDO_USER:-$USER}
SERVICE_FILE="/home/$ACTUAL_USER/Documents/GitHub/ishara-iot/fish-streaming.service"
SYSTEMD_PATH="/etc/systemd/system/fish-streaming.service"

echo "Installing systemd service..."

# Copy service file to systemd
if [ -f "$SERVICE_FILE" ]; then
    cp "$SERVICE_FILE" "$SYSTEMD_PATH"
    echo "✓ Service file copied to $SYSTEMD_PATH"
else
    echo "✗ Service file not found at $SERVICE_FILE"
    exit 1
fi

# Reload systemd daemon
echo "Reloading systemd daemon..."
systemctl daemon-reload

# Enable service to start on boot
echo "Enabling service to start on boot..."
systemctl enable fish-streaming.service

# Start service now
echo "Starting service..."
systemctl start fish-streaming.service

echo ""
echo "=================================================="
echo "Auto-Start Setup Complete!"
echo "=================================================="
echo ""
echo "Service Status:"
systemctl status fish-streaming.service --no-pager -l
echo ""
echo "Useful Commands:"
echo "  Check status:    sudo systemctl status fish-streaming.service"
echo "  View logs:       sudo journalctl -u fish-streaming.service -f"
echo "  Stop service:    sudo systemctl stop fish-streaming.service"
echo "  Start service:   sudo systemctl start fish-streaming.service"
echo "  Restart service: sudo systemctl restart fish-streaming.service"
echo "  Disable auto-start: sudo systemctl disable fish-streaming.service"
echo ""
echo "The streaming server will now automatically start on boot!"
echo "Server URL: http://192.168.8.101:5000"
echo ""
