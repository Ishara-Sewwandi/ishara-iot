# ✅ LiveKit Auto-Start Configuration Complete

## Current Status

### ✅ Configured Services
- **LiveKit Publisher**: `ENABLED` - Will auto-start on boot
- **Flask Streaming**: `DISABLED` - Will NOT auto-start
- **Other Services**: None configured for auto-start

### 🔴 Current Issue
**WebRTC Connection Timeout**: `wait_pc_connection timed out`

**Symptom**: Live feed shows black screen in dashboard

**Cause**: LiveKit server on VPS needs ICE/TURN configuration for NAT traversal

The Raspberry Pi **cannot establish WebRTC peer connection** to LiveKit server. WebSocket signaling works, but media connection fails.

## What Works Now

✅ **Auto-Start on Boot**: LiveKit service will automatically start when Raspberry Pi boots
✅ **Camera & Detection**: Both YOLOv8 models load successfully
✅ **Service Management**: Only LiveKit runs, Flask streaming is disabled
✅ **Auto-Reconnect**: Service will keep trying to connect every 10-20 seconds

## What Needs To Be Fixed

### On Your VPS (187.77.189.5)

Your **LiveKit server needs ICE/TURN configuration** for WebRTC to work.

See the detailed troubleshooting guide:
```
LIVEKIT_TROUBLESHOOTING.md
```

**Required fixes on VPS:**
1. Open UDP ports 50000-60000 in firewall
2. Configure TURN server in `livekit.yaml`
3. Set `external_ip: 187.77.189.5` in LiveKit config
4. Restart LiveKit service

**The issue is NOT on Raspberry Pi** - everything here is working correctly.

Once VPS LiveKit is configured, the video feed will appear automatically.

## Useful Commands

### Check Status
```bash
./check_livekit_status.sh
```

### View Live Logs
```bash
sudo journalctl -u livekit-publisher.service -f
```

### Restart Service
```bash
sudo systemctl restart livekit-publisher.service
```

### Stop Service
```bash
sudo systemctl stop livekit-publisher.service
```

### Start Service
```bash
sudo systemctl start livekit-publisher.service
```

### Disable Auto-Start (if needed)
```bash
sudo systemctl disable livekit-publisher.service
```

### Enable Auto-Start Again
```bash
sudo systemctl enable livekit-publisher.service
```

## Test Reboot

To verify auto-start works:
```bash
sudo reboot
```

After reboot, check status:
```bash
./check_livekit_status.sh
```

The service should be running automatically (but will show SSL error until VPS is fixed).

## Expected Behavior After VPS Fix

Once LiveKit server on VPS is properly configured with ICE/TURN, you'll see:

**In Raspberry Pi logs:**
```
✅ Connected to LiveKit room: boat-navigation
✅ Video track published (TR_xxxxxxxxxxxxx)
🎬 Publishing to LiveKit at up to 15 FPS...
📡 Frames: 150 | FPS: 14.8 | Detections: 3
```

**In your dashboard:**
- Live video feed with fish detection overlays
- Real-time detection annotations
- Smooth streaming from anywhere

## Architecture

```
Raspberry Pi (192.168.8.101)
    ↓ (Auto-start on boot)
livekit_publisher.py
    ↓ (Fish Detection + Camera)
    ↓ (WebRTC Stream)
    ↓ (wss:// - SSL/TLS)
Traefik Reverse Proxy
    ↓ (VPS: 187.77.189.5)
LiveKit Server
    ↓ (room: boat-navigation)
Your Frontend/Backend
```

## Files Modified

- `/etc/systemd/system/livekit-publisher.service` - Auto-start configuration
- `.env` - LiveKit credentials
- `livekit_publisher.py` - Main streaming application
- `check_livekit_status.sh` - Status checking script (NEW)

## Next Steps

1. **Fix LiveKit server on VPS** (see `LIVEKIT_TROUBLESHOOTING.md` for detailed steps)
   - Configure ICE/TURN in `livekit.yaml`
   - Open UDP ports 50000-60000
   - Set external_ip to 187.77.189.5
   - Restart LiveKit: `docker restart <livekit-container>`

2. **Verify connection** - Raspberry Pi will connect automatically
   ```bash
   sudo journalctl -u livekit-publisher.service -f
   ```

3. **Check dashboard** - Live video feed will appear with fish detection

4. **Test reboot**: `sudo reboot` to verify auto-start

**Alternative (Easier)**: Use LiveKit Cloud instead of self-hosting
- Sign up at https://cloud.livekit.io
- Get API credentials
- Update `.env` with cloud URL and credentials
- No NAT/firewall issues to worry about

---

**Service is running and will auto-start on boot!** 🚀

**Live feed is black because**: VPS LiveKit server cannot establish WebRTC connection (NAT traversal issue)

**Fix**: Configure ICE/TURN on VPS LiveKit server (see `LIVEKIT_TROUBLESHOOTING.md`)
