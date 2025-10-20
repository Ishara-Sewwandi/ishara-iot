#!/bin/bash

# Installation script for Raspberry Pi 4

echo "=================================="
echo "Fish Mortality Detection System"
echo "Installation for Raspberry Pi 4"
echo "=================================="

# Update system
echo "Updating system..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo "Installing system dependencies..."
sudo apt install -y python3-pip python3-opencv
sudo apt install -y libcap-dev libatlas-base-dev
sudo apt install -y libjpeg-dev libtiff5-dev libpng-dev
sudo apt install -y libavcodec-dev libavformat-dev libswscale-dev
sudo apt install -y libv4l-dev libxvidcore-dev libx264-dev
sudo apt install -y python3-dev python3-numpy

# Install Picamera2
echo "Installing Picamera2..."
sudo apt install -y python3-picamera2

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p alerts/images
mkdir -p logs
mkdir -p models

# Enable camera interface
echo "Enabling camera interface..."
sudo raspi-config nonint do_camera 0

# Setup .env file template
if [ ! -f .env ]; then
    echo "Creating .env template..."
    cat > .env << EOL
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Webhook Configuration
WEBHOOK_URL=https://your-api.com/alerts

# Email Configuration (optional)
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient@email.com
EMAIL_PASSWORD=your_app_password
EOL
    echo "✓ .env template created - please edit with your credentials"
fi

# Make scripts executable
chmod +x main.py
chmod +x test_*.py
chmod +x train_model.py

echo ""
echo "=================================="
echo "Installation Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials"
echo "2. Configure config.py settings"
echo "3. Reboot your Raspberry Pi: sudo reboot"
echo "4. Test camera: python3 test_camera.py"
echo "5. Train or download YOLOv8 model"
echo "6. Run system: python3 main.py"
echo ""
echo "Documentation: README.md"
echo "=================================="
