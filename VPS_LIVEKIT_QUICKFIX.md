# Quick Fix: LiveKit VPS Configuration

## Problem
Live feed shows black screen because **WebRTC connection times out**.

Error: `wait_pc_connection timed out`

## Why This Happens
LiveKit server on your VPS needs proper configuration for **NAT traversal**. Without it, the Raspberry Pi can't establish a WebRTC peer connection even though WebSocket signaling works.

## Quick Fix Steps

### Step 1: SSH to VPS
```bash
ssh user@187.77.189.5
cd /home/koi/Documents/GitHub/koi-fish-friend
```

### Step 2: Check Current LiveKit Configuration

Find your LiveKit configuration file (one of these):
```bash
# Check docker-compose.yml
cat docker-compose.yml | grep -A 20 livekit

# Check for livekit.yaml
find . -name "livekit.yaml" -o -name "config.yaml"
```

### Step 3: Update LiveKit Configuration

Edit `livekit.yaml` (or create it):
```yaml
port: 7880
bind_addresses:
  - 0.0.0.0

# CRITICAL: Add this for NAT traversal
rtc:
  # Port range for WebRTC media
  port_range_start: 50000
  port_range_end: 60000
  
  # Your VPS public IP (REQUIRED)
  node_ip: 187.77.189.5
  
  # Use external IP for ICE candidates
  use_external_ip: true

# Enable debug logging temporarily
logging:
  level: debug
```

### Step 4: Open Firewall Ports on VPS
```bash
# Allow WebRTC media ports (UDP - CRITICAL)
sudo ufw allow 50000:60000/udp

# Allow LiveKit server (already open, but verify)
sudo ufw allow 7880/tcp

# Check status
sudo ufw status | grep -E "7880|50000"
```

### Step 5: Restart LiveKit

If using Docker:
```bash
docker ps | grep livekit
docker restart <livekit-container-name>

# Watch logs
docker logs -f <livekit-container-name>
```

If using systemd:
```bash
sudo systemctl restart livekit
sudo journalctl -u livekit -f
```

### Step 6: Verify Configuration

Look for these in LiveKit logs:
```
✅ "using external IP: 187.77.189.5"
✅ "ICE server configured"
✅ "UDP ports 50000-60000 bound"
```

### Step 7: Test from Raspberry Pi

The service should connect automatically within 5-20 seconds:
```bash
# On Raspberry Pi
sudo journalctl -u livekit-publisher.service -f
```

Expected output:
```
✅ Connected to LiveKit room: boat-navigation
✅ Video track published (TR_xxxxxxxxxxxxx)
🎬 Publishing to LiveKit at up to 15 FPS...
```

## Alternative: Use LiveKit Cloud (Recommended)

If self-hosting is too complex, use LiveKit's managed service:

### 1. Sign up at LiveKit Cloud
https://cloud.livekit.io (free tier available)

### 2. Create a project and get credentials
- Project URL: `wss://your-project.livekit.cloud`
- API Key: `APIxxxxxxxxx`
- API Secret: `xxxxxxxxxxxxxxxxx`

### 3. Update Raspberry Pi configuration
```bash
# On Raspberry Pi
cd /home/koi/Documents/GitHub/ishara-iot
nano .env
```

Update these lines:
```bash
export LIVEKIT_URL=wss://your-project.livekit.cloud
export LIVEKIT_API_KEY=APIxxxxxxxxx
export LIVEKIT_API_SECRET=xxxxxxxxxxxxxxxxx
```

### 4. Restart service
```bash
sudo systemctl restart livekit-publisher.service
```

### 5. Verify
```bash
sudo journalctl -u livekit-publisher.service -f
```

**Benefits of LiveKit Cloud:**
- ✅ No NAT/firewall configuration needed
- ✅ Global TURN servers included
- ✅ Automatic scaling
- ✅ Better reliability
- ✅ Free tier for testing

## Verification Checklist

After fixing VPS or switching to cloud:

- [ ] Raspberry Pi logs show "Connected to LiveKit room"
- [ ] Dashboard shows live video feed (not black)
- [ ] Fish detection overlays visible
- [ ] Can view from anywhere (not just local network)
- [ ] Auto-start works after reboot

## Common Issues

### Issue: Still timing out after firewall changes
**Solution**: Verify LiveKit is actually using the ports:
```bash
sudo netstat -tulpn | grep -E "7880|50000"
```

### Issue: "Connection refused" instead of timeout
**Solution**: LiveKit service not running:
```bash
docker ps | grep livekit
# or
sudo systemctl status livekit
```

### Issue: Works locally but not remotely
**Solution**: External IP not configured correctly. Verify `node_ip` in config.

## Need Help?

Check these files for detailed troubleshooting:
- `LIVEKIT_TROUBLESHOOTING.md` - Comprehensive debugging guide
- `LIVEKIT_AUTOSTART_COMPLETE.md` - Configuration status

VPS LiveKit server is the issue, not Raspberry Pi!
