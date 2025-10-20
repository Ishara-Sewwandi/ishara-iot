# Quick Start - Live Camera Display

## 🎥 View Live Camera Feed

### Option 1: Full Monitoring System with Display
```bash
cd /home/koi/Documents/GitHub/ishara-iot
./start.sh
```
- Shows live feed with fish detection
- Monitors behavior and sends alerts
- Press **'q'** to quit

### Option 2: Live View Only (Testing)
```bash
python3 live_view.py
```
- Just camera + fish detection overlay
- No behavior monitoring or alerts
- Press **'q'** to quit, **'s'** to screenshot

### Option 3: Headless Mode (No Display)
Edit `config.py`:
```python
DISPLAY_ENABLED = False
```
Then: `./start.sh`

## 📊 What You'll See

### Display Elements:
- **Top Panel**: System info, frame count, fish count, time
- **Fish Boxes**: 
  - 🟢 Green = Healthy
  - 🔴 Red = Mortality signs
  - 🟡 Yellow = Analyzing
- **Behavior Metrics**: Fin activity %, Movement %, Side-floating alert
- **Bottom Bar**: System status

### Example Display:
```
┌──────────────────────────────────────────┐
│ Fish Mortality Detection System          │
│ Frame: 1234  Fish: 3  Time: 14:32:15    │
│ Press 'q' to quit                         │
├──────────────────────────────────────────┤
│                                           │
│     ┌─────────┐                          │
│     │ Fish #1 │ (Green box)               │
│     │ Fin: 82%│                           │
│     │ Move: 75%                           │
│     └─────────┘                          │
│                                           │
│           ┌─────────┐                    │
│           │ Fish #2 │ (Red box)          │
│           │ Fin: 15%│                    │
│           │ Move: 10%                     │
│           │ SIDE FLOATING! ⚠️            │
│           └─────────┘                    │
│                                           │
├──────────────────────────────────────────┤
│ SYSTEM: ACTIVE                           │
└──────────────────────────────────────────┘
```

## ⚙️ Configuration

All settings in `config.py`:
```python
# Toggle display on/off
DISPLAY_ENABLED = True

# Display window size
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720

# Camera settings
CAMERA_WIDTH = 1920
CAMERA_HEIGHT = 1080
FRAME_RATE = 10
```

## 🐛 Quick Troubleshooting

**No display appears:**
```bash
export DISPLAY=:0
./start.sh
```

**Laggy/slow:**
- Lower resolution in `config.py`
- Reduce `FRAME_RATE` to 5
- Check CPU: `htop`

**Camera not working:**
```bash
libcamera-hello  # Test camera
vcgencmd get_camera  # Check status
```

## 📝 Files Created

- **`main.py`** - Updated with display features
- **`live_view.py`** - Standalone viewer
- **`config.py`** - Added DISPLAY_ENABLED setting
- **`DISPLAY_GUIDE.md`** - Full documentation
- **`README.md`** - Updated with display instructions

## 🎯 Next Steps

1. ✅ System now shows live feed
2. Configure alert credentials in `.env`
3. Train custom fish detection model
4. Set up as systemd service for auto-start

---

**Need help?** See DISPLAY_GUIDE.md for details!
