#!/bin/bash
# Setup script to enable auto-start on boot for LiveKit Fish Detection Publisher

echo "============================================================"
echo "LiveKit Fish Detection Publisher - Auto-Start Setup"
echo "============================================================"
echo ""

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "Please run with sudo:"
    echo "sudo ./setup_livekit_autostart.sh"
    exit 1
fi

# Get the actual user (not root)
ACTUAL_USER=${SUDO_USER:-$USER}
SERVICE_FILE="/home/$ACTUAL_USER/Documents/GitHub/ishara-iot/livekit-publisher.service"
SYSTEMD_PATH="/etc/systemd/system/livekit-publisher.service"

echo "Installing LiveKit dependencies..."

# Check if venv exists, if not create it
VENV_PATH="/home/$ACTUAL_USER/Documents/GitHub/ishara-iot/venv"
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating Python virtual environment..."
    sudo -u $ACTUAL_USER python3 -m venv "$VENV_PATH"
fi

# Install LiveKit packages
echo "Installing livekit and livekit-api..."
sudo -u $ACTUAL_USER "$VENV_PATH/bin/pip" install --upgrade pip
sudo -u $ACTUAL_USER "$VENV_PATH/bin/pip" install livekit livekit-api

echo ""
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
systemctl enable livekit-publisher.service

# Start service now
echo "Starting service..."
systemctl start livekit-publisher.service

echo ""
echo "============================================================"
echo "LiveKit Auto-Start Setup Complete!"
echo "============================================================"
echo ""
echo "Service Status:"
systemctl status livekit-publisher.service --no-pager -l
echo ""
echo "Useful Commands:"
echo "  Check status:      sudo systemctl status livekit-publisher.service"
echo "  View live logs:    sudo journalctl -u livekit-publisher.service -f"
echo "  Stop service:      sudo systemctl stop livekit-publisher.service"
echo "  Start service:     sudo systemctl start livekit-publisher.service"
echo "  Restart service:   sudo systemctl restart livekit-publisher.service"
echo "  Disable auto-start: sudo systemctl disable livekit-publisher.service"
echo ""
echo "The LiveKit publisher will now automatically start on boot!"
echo "LiveKit Server: wss://livekit.koifish-livekit-9ae13d-187-77-189-5.traefik.me"
echo "Room: boat-navigation"
echo ""
