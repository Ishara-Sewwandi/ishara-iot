# Live Camera Display Guide

## Overview
The system now includes a **real-time visual display** showing the camera feed with overlays for fish detection and behavior analysis.

## Features

### Visual Indicators

#### Fish Detection Boxes
- 🟢 **Green Box** - Healthy fish (normal behavior)
- 🔴 **Red Box** - Mortality indicators detected (alert!)
- 🟡 **Yellow Box** - Fish detected, behavior analysis in progress

#### Information Display
- **Top Panel** - System status and statistics
  - Frame count
  - Number of fish detected
  - Current time
  - Quit instructions

- **Per-Fish Metrics**
  - Fish ID number
  - Fin activity percentage
  - Movement score
  - Side-floating warning (if detected)

- **Bottom Status Bar**
  - System active indicator

## How to Use

### 1. Run with Live Display

```bash
cd /home/koi/Documents/GitHub/ishara-iot
./start.sh
```

The display window will open automatically showing the live camera feed.

### 2. Run Live View Only (Testing)

For testing camera and detection without running the full monitoring system:

```bash
python3 live_view.py
```

**Controls for live_view.py:**
- Press **'q'** - Quit application
- Press **'s'** - Save screenshot to `alerts/images/`

### 3. Run Headless (No Display)

For running on a server or headless Raspberry Pi:

Edit `config.py`:
```python
DISPLAY_ENABLED = False
```

Then run:
```bash
./start.sh
```

### 4. Remote Display via SSH

If accessing Raspberry Pi remotely via SSH:

```bash
# With X11 forwarding
ssh -X pi@raspberrypi.local
cd /home/koi/Documents/GitHub/ishara-iot
./start.sh

# Or using VNC
# Connect via VNC viewer, then run normally
```

## Display Configuration

Edit `config.py` to customize:

```python
# Display Settings
DISPLAY_ENABLED = True          # Enable/disable display
DISPLAY_WIDTH = 1280            # Display window width
DISPLAY_HEIGHT = 720            # Display window height

# Camera Settings
CAMERA_WIDTH = 1920             # Camera resolution
CAMERA_HEIGHT = 1080
FRAME_RATE = 10                 # Frames per second
```

## Understanding the Display

### Healthy Fish Example
```
┌─────────────────────────┐
│ Fish #1                 │ ← Green box
│                         │
│ Fin: 85%    ✓           │ ← High fin activity (good)
│ Move: 72%   ✓           │ ← Good movement (healthy)
└─────────────────────────┘
```

### Unhealthy Fish Example
```
┌─────────────────────────┐
│ Fish #2                 │ ← Red box
│                         │
│ Fin: 12%    ✗           │ ← Low fin activity (bad)
│ Move: 8%    ✗           │ ← Minimal movement (bad)
│ SIDE FLOATING! ⚠️       │ ← Alert indicator
└─────────────────────────┘
```

## Performance Tips

### Improve FPS
If display is laggy:

1. **Lower camera resolution:**
   ```python
   CAMERA_WIDTH = 1280
   CAMERA_HEIGHT = 720
   ```

2. **Reduce frame rate:**
   ```python
   FRAME_RATE = 5  # Lower FPS = better performance
   ```

3. **Smaller display window:**
   ```python
   DISPLAY_WIDTH = 800
   DISPLAY_HEIGHT = 600
   ```

### Optimize for Raspberry Pi 4
```python
# Recommended settings for smooth display
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
FRAME_RATE = 10
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720
```

## Troubleshooting

### Display not showing

**Issue:** Window doesn't open
**Solution:**
```bash
# Check if DISPLAY is set
echo $DISPLAY

# Set display
export DISPLAY=:0

# Or run with display explicitly
DISPLAY=:0 python3 main.py
```

### "Can't connect to X server" error

**Solution:**
```bash
# Install X11 packages
sudo apt install -y xserver-xorg

# Or use VNC instead
sudo apt install -y realvnc-vnc-server
sudo systemctl enable vncserver-x11-serviced
sudo systemctl start vncserver-x11-serviced
```

### Low FPS / Laggy display

**Solution:**
1. Lower resolution (see Performance Tips above)
2. Close other applications
3. Check CPU usage: `htop`
4. Consider running headless if display not needed

### No camera detected

**Solution:**
```bash
# Test camera
libcamera-hello

# Check connections
vcgencmd get_camera

# Enable camera interface
sudo raspi-config
# Interface Options > Camera > Enable
sudo reboot
```

## Screenshots

Screenshots are saved to:
```
alerts/images/screenshot_YYYYMMDD_HHMMSS.jpg
```

## Advanced Usage

### Custom Display Layout

To customize the display, edit the `_draw_display()` method in `main.py`:

```python
def _draw_display(self, frame, detections, analysis_results, frame_count):
    # Add your custom overlays here
    # cv2.putText(...) for text
    # cv2.rectangle(...) for boxes
    # cv2.circle(...) for indicators
    return display
```

### Record Video

To record the display output:

```python
# In main.py, add after creating window:
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, 10.0, (1280, 720))

# In display loop, add:
out.write(display_frame)

# Before cleanup:
out.release()
```

## FAQ

**Q: Can I run this remotely?**
A: Yes, use SSH with X11 forwarding or VNC.

**Q: Does display affect detection performance?**
A: Minimal impact. Drawing overlays is computationally light.

**Q: Can I hide certain overlays?**
A: Yes, edit `_draw_display()` in `main.py` to customize.

**Q: How do I save the display feed?**
A: Use OpenCV's VideoWriter (see Advanced Usage above).

**Q: Can I stream this to a web browser?**
A: Yes, you can use Flask + OpenCV to stream MJPEG. (Future feature)

---

**For more help:**
- Check main README.md
- View logs: `tail -f fish_monitoring.log`
- Report issues on GitHub
