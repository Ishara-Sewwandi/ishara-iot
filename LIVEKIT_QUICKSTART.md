# 🐟 LiveKit Fish Detection - Quick Start

## 🚀 Setup in 3 Steps

### 1️⃣ Install Dependencies
```bash
cd /home/koi/Documents/GitHub/ishara-iot
source venv/bin/activate
pip install livekit livekit-api
```

### 2️⃣ Test Run
```bash
./start_livekit_publisher.sh
```

### 3️⃣ Enable Auto-Start on Boot
```bash
sudo ./setup_livekit_autostart.sh
```

**Done!** 🎉 Your Pi will now stream fish detection to LiveKit on every boot.

---

## 📺 View the Stream

### From Your Dashboard
Open your Spring Boot dashboard and navigate to room: `boat-navigation`

### From Browser (Testing)
Access the LiveKit server: `wss://livekit.koifish-livekit-9ae13d-187-77-189-5.traefik.me`

---

## 🔧 Management

```bash
# Check status
sudo systemctl status livekit-publisher.service

# View live logs
sudo journalctl -u livekit-publisher.service -f

# Restart
sudo systemctl restart livekit-publisher.service

# Stop
sudo systemctl stop livekit-publisher.service
```

---

## 📖 Full Documentation

- **Complete Setup**: `LIVEKIT_SETUP_GUIDE.md`
- **Comparison**: `STREAMING_COMPARISON.md`
- **Original Guide**: `AUTOSTART_GUIDE.md`

---

## ⚙️ Configuration

Edit `.env` file or modify `livekit_publisher.py`:

```bash
LIVEKIT_URL=wss://livekit.koifish-livekit-9ae13d-187-77-189-5.traefik.me
LIVEKIT_API_KEY=APIhfro22ogg9c3
LIVEKIT_API_SECRET=5ejwe0usuxnlknv5afgtsyfvsgmukb1pedprwwqaxilc
LIVEKIT_ROOM=boat-navigation
```

---

## 🎯 What You Get

- ✅ Real-time fish detection on live video
- ✅ Health classification (healthy/diseased)
- ✅ Streaming from any network (local, remote, mobile)
- ✅ Automatic reconnection if connection drops
- ✅ Auto-start on Raspberry Pi boot
- ✅ Detection overlays with color-coded health status

---

## 🐛 Troubleshooting

### Can't connect to LiveKit?
```bash
# Check internet
ping -c 3 google.com

# Check LiveKit server
curl -s https://livekit.koifish-livekit-9ae13d-187-77-189-5.traefik.me
```

### Camera not found?
```bash
# List cameras
ls /dev/video*

# Test camera
v4l2-ctl --device=/dev/video0 --all
```

### Low FPS?
```bash
# Use lower resolution
python3 livekit_publisher.py --width 480 --height 360 --fps 10
```

---

## 📞 Need Help?

Check the full guides:
- `LIVEKIT_SETUP_GUIDE.md` - Complete setup instructions
- `STREAMING_COMPARISON.md` - Compare Flask vs LiveKit
- `AUTOSTART_GUIDE.md` - Auto-start configuration

---

**Happy Fish Monitoring! 🐟📹**
