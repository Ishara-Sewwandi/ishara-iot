# LiveKit Connection Troubleshooting

## Current Status

### ✅ What's Working
- **SSL Certificate**: Valid Let's Encrypt certificate on `livekit.koifishfriend.online`
- **LiveKit Server**: Reachable and responding (returns `OK`)
- **Auto-Start**: Service configured correctly and running
- **Camera & Models**: Both fish detection models loading successfully
- **API Credentials**: Correct API key and secret
- **Network**: VPS reachable, ping working

### ❌ Current Issue
**Error**: `wait_pc_connection timed out`

**Meaning**: WebRTC peer connection timeout - the signaling succeeds, but the media (WebRTC) connection fails to establish.

## Root Cause Analysis

The error "`wait_pc_connection timed out`" indicates that:
1. ✅ WebSocket connection to LiveKit server **succeeds**
2. ✅ Token authentication **succeeds**
3. ❌ WebRTC peer connection **fails to establish**

This is a **NAT traversal / firewall issue**, not a configuration problem on the Raspberry Pi.

## What Needs To Be Fixed on VPS

### Issue: LiveKit Server Missing ICE/TURN Configuration

According to the deployment guide, your LiveKit server should have:
- **TURN server** at `livekit-turn.koifish-livekit-57c0a8-187-77-189-5.traefik.me:5349`
- **Proper ICE server configuration**

But currently, the LiveKit server isn't providing proper ICE candidates for NAT traversal.

### Solution: Configure LiveKit Server

You need to check/fix your LiveKit server configuration on the VPS at `/home/koi/Documents/GitHub/koi-fish-friend`.

#### 1. Check LiveKit Configuration

SSH to VPS:
```bash
ssh user@187.77.189.5
cd /home/koi/Documents/GitHub/koi-fish-friend
```

Check `livekit.yaml` or `docker-compose.yml` for LiveKit configuration.

#### 2. Required LiveKit Configuration

Your `livekit.yaml` should include:

```yaml
port: 7880
bind_addresses:
  - 0.0.0.0

# CRITICAL: Add ICE/TURN configuration
rtc:
  # Port range for WebRTC connections
  port_range_start: 50000
  port_range_end: 60000
  
  # Use mDNS for local discovery
  use_external_ip: true
  
  # Your VPS public IP
  node_ip: 187.77.189.5
  
  # TURN server configuration (for NAT traversal)
  turn_servers:
    - host: livekit.koifishfriend.online
      port: 5349
      protocol: tls
      username: livekit
      credential: your-turn-secret

# Logging
logging:
  level: info
```

#### 3. Open Required Ports on VPS

```bash
# WebRTC media ports (UDP)
sudo ufw allow 50000:60000/udp

# LiveKit server (TCP)
sudo ufw allow 7880/tcp

# TURN server (TCP/UDP)
sudo ufw allow 5349/tcp
sudo ufw allow 5349/udp

# Verify
sudo ufw status
```

#### 4. Verify LiveKit is Using External IP

In your LiveKit logs on VPS, you should see:
```bash
docker logs <livekit-container-name>
```

Look for:
- `using external IP: 187.77.189.5`
- `TURN server listening on port 5349`

#### 5. Alternative: Use LiveKit Cloud (Easier)

If self-hosting is too complex, use LiveKit Cloud:

1. Sign up at https://cloud.livekit.io
2. Get new API credentials
3. Update `.env` on Raspberry Pi:
   ```bash
   LIVEKIT_URL=wss://your-project.livekit.cloud
   LIVEKIT_API_KEY=<your-cloud-api-key>
   LIVEKIT_API_SECRET=<your-cloud-api-secret>
   ```
4. Restart: `sudo systemctl restart livekit-publisher.service`

LiveKit Cloud handles all NAT traversal automatically.

## Quick Test: Verify TURN Server

From Raspberry Pi, test if TURN server is accessible:

```bash
# Test TCP connection
nc -zv 187.77.189.5 5349

# Test UDP (harder to test, but check firewall)
sudo nmap -sU -p 50000-50010 187.77.189.5
```

## Check VPS LiveKit Logs

```bash
# If using Docker
docker logs <livekit-container> --tail 100 -f

# If using systemd
sudo journalctl -u livekit.service -f
```

Look for errors about:
- ICE candidate gathering
- TURN server failures
- Port binding issues

## Comparison: What's Different?

| Component | Expected (from guide) | Current Status |
|-----------|----------------------|----------------|
| SSL Certificate | ✅ Let's Encrypt | ✅ Let's Encrypt |
| WebSocket URL | `wss://livekit.koifishfriend.online` | ✅ Correct |
| HTTP Health Check | Returns `OK` | ✅ Working |
| TURN Server | `livekit-turn...traefik.me:5349` | ❓ Unknown |
| UDP Ports | 50000-60000 open | ❓ Likely blocked |
| WebRTC Connection | ✅ Should work | ❌ Timeout |

## Next Steps

### Immediate Action Required (on VPS):

1. **Check LiveKit configuration** for ICE/TURN settings
2. **Open UDP ports** 50000-60000 on VPS firewall
3. **Verify TURN server** is running and accessible
4. **Check LiveKit logs** for ICE/TURN errors
5. **Restart LiveKit** after configuration changes

### On Raspberry Pi (Already Done):

✅ Configuration correct
✅ Service auto-start enabled
✅ SSL certificate trusted
✅ Camera and models working
✅ Will connect automatically once VPS is fixed

## Expected Behavior After Fix

Once VPS LiveKit server is properly configured:

```
2026-03-07 04:XX:XX [INFO] Connecting to LiveKit: wss://livekit.koifishfriend.online
2026-03-07 04:XX:XX [INFO] ✅ Connected to LiveKit room: boat-navigation
2026-03-07 04:XX:XX [INFO] ✅ Video track published (TR_xxxxxxxxxxxxx)
2026-03-07 04:XX:XX [INFO] 🎬 Publishing to LiveKit at up to 15 FPS...
2026-03-07 04:XX:XX [INFO] 📡 Frames: 150 | FPS: 14.8 | Detections: 3
```

## Resources

- LiveKit Self-Hosting Docs: https://docs.livekit.io/deploy/
- TURN Server Setup: https://docs.livekit.io/deploy/turn-servers/
- NAT Traversal Guide: https://docs.livekit.io/deploy/nat-traversal/
- LiveKit Cloud (easier): https://cloud.livekit.io

---

**Summary**: The Raspberry Pi is working perfectly. The issue is on the VPS - LiveKit server needs proper ICE/TURN configuration for WebRTC to work through NAT.
