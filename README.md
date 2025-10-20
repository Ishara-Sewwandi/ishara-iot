# Fish Mortality Detection System

Advanced IoT system for early detection of fish mortality in aquaculture using Raspberry Pi 4 and Pi Camera Module 2.

## Features

🐟 **Fish Behavior Analysis**
- YOLOv8-based fish detection
- Fin activity monitoring using optical flow
- Side-floating behavior detection
- Movement pattern analysis

🌧️ **Rainfall Detection**
- Hardware sensor support (GPIO)
- Visual rainfall detection using computer vision
- Real-time weather alerts

📱 **Multi-Channel Alerts**
- Telegram notifications with images
- Email alerts
- Webhook integration for web/mobile apps
- Image evidence for all alerts

## Hardware Requirements

- Raspberry Pi 4 Model B
- Pi Camera Module 2
- (Optional) Rainfall sensor connected to GPIO
- SD card (32GB+ recommended)
- Power supply

## Software Requirements

```bash
Python 3.9+
OpenCV
YOLOv8 (Ultralytics)
Picamera2
RPi.GPIO
```

## Installation

### 1. System Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3-pip python3-opencv
sudo apt install -y libcap-dev libatlas-base-dev
sudo apt install -y python3-picamera2
```

### 2. Install Python Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Configure Camera

```bash
# Enable camera interface
sudo raspi-config
# Navigate to: Interface Options > Camera > Enable

# Reboot
sudo reboot
```

### 4. Configuration

Create a `.env` file with your credentials:

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Webhook
WEBHOOK_URL=https://your-api.com/alerts

# Email (optional)
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient@email.com
EMAIL_PASSWORD=your_app_password
```

Edit `config.py` to customize:
- Camera resolution and frame rate
- Detection thresholds
- Alert intervals
- GPIO pin assignments

## Usage

### Basic Usage

```bash
# RECOMMENDED: Stable 25 FPS viewer (optimized)
python3 live_view_25fps.py

# Ultra-smooth viewer (25-30 FPS)
python3 live_view_smooth.py

# Full system with live display
./start.sh

# Interactive menu (all options)
./menu.sh

# Run live view only (testing)
python3 live_view.py

# Run without display (headless mode)
# Edit config.py and set DISPLAY_ENABLED = False
python3 main.py
```

**Live Display Controls:**
- Press **'q'** to quit
- Press **'s'** to save screenshot
- Press **'d'** to toggle detection (for max FPS)
- Press **'f'** for fullscreen
- Visual indicators:
  - 🟢 **Green box** = Healthy fish
  - 🔴 **Red box** = Mortality indicators detected
  - 🟡 **Yellow box** = Fish detected, analyzing...

**Performance Modes:**
- `live_view_25fps.py` - Stable 24-25 FPS (most consistent)
- `live_view_smooth.py` - 25-30 FPS (highest FPS)
- `main.py` - Full monitoring with display

### Train Custom YOLOv8 Model

```bash
# Collect and label training data of your fish
# Use Roboflow or labelImg for annotation

# Train YOLOv8
python3 train_model.py --data fish_dataset.yaml --epochs 100

# Update config.py with your model path
```

### Test Individual Components

```bash
# Test camera
python3 test_camera.py

# Test fish detection
python3 test_detector.py

# Test alerts
python3 test_alerts.py
```

## System Architecture

```
┌─────────────────┐
│  Pi Camera      │
│  Module 2       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Camera Handler  │
│ (Picamera2)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│ Fish Detector   │─────▶│ Behavior Analyzer│
│ (YOLOv8)        │      │ (Optical Flow)   │
└─────────────────┘      └────────┬─────────┘
                                  │
         ┌────────────────────────┘
         ▼
┌─────────────────┐      ┌──────────────────┐
│ Mortality       │─────▶│  Alert System    │
│ Detection       │      │  (Multi-channel) │
└─────────────────┘      └──────────────────┘
         │
         ▼
┌─────────────────┐
│ Rainfall        │
│ Detection       │
└─────────────────┘
```

## Behavior Detection Methods

### 1. Fin Activity Analysis
- Uses Farneback optical flow algorithm
- Detects movement in fin regions
- Threshold: < 30% activity triggers alert

### 2. Side-Floating Detection
- Ellipse fitting on fish contours
- Orientation angle analysis
- Detects abnormal vertical orientation

### 3. Movement Score
- Tracks fish position over time
- Calculates displacement between frames
- Low movement indicates potential issues

## Rainfall Detection

### Hardware Sensor
- Connects to GPIO pin (default: GPIO 17)
- Active LOW when rain detected

### Visual Detection
- Analyzes vertical streak patterns
- Temporal change detection
- Texture analysis for rain patterns

## Alert Configuration

Modify `config.py` for alert customization:

```python
# Alert thresholds
FIN_ACTIVITY_THRESHOLD = 0.3
MOVEMENT_THRESHOLD = 0.2

# Alert intervals
RAINFALL_ALERT_COOLDOWN = 300  # 5 minutes

# Methods: "telegram", "web", "both"
ALERT_METHOD = "both"
```

## Troubleshooting

### Camera Issues
```bash
# Check camera status
vcgencmd get_camera

# Test with libcamera
libcamera-hello
```

### Performance Issues
- Reduce camera resolution in `config.py`
- Lower frame rate
- Use lighter YOLOv8 model (yolov8n.pt)

### GPIO Issues
```bash
# Check GPIO permissions
sudo usermod -a -G gpio $USER
```

## Performance Optimization

### For Raspberry Pi 4
- Recommended resolution: 1280x720 @ 10fps
- Use YOLOv8n (nano) model for faster inference
- Enable hardware acceleration if available

### Memory Management
- System automatically cleans old images
- Configure `MAX_STORED_IMAGES` in config
- Monitor with: `free -h`

## API Integration

### Webhook Payload Format

```json
{
  "type": "mortality|rainfall",
  "message": "Alert details...",
  "timestamp": "2025-10-20T10:30:00",
  "image_path": "/path/to/image.jpg"
}
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Test thoroughly on Raspberry Pi
4. Submit pull request

## License

MIT License - See LICENSE file

## Support

For issues and questions:
- GitHub Issues: [repository]/issues
- Email: support@example.com

## Acknowledgments

- YOLOv8 by Ultralytics
- Picamera2 library
- OpenCV community

## Citation

If you use this system in research, please cite:

```bibtex
@software{fish_mortality_detection,
  title={Fish Mortality Detection System},
  author={Your Name},
  year={2025},
  url={https://github.com/yourusername/ishara-iot}
}
```

---

**Version:** 1.0.0  
**Last Updated:** October 2025  
**Status:** Production Ready
