# Auto-Start Setup Guide for Fish Streaming Server

## 🚀 Quick Setup

To enable the streaming server to automatically start when Raspberry Pi boots:

```bash
sudo ./setup_autostart.sh
```

## 📋 What This Does

1. Creates a systemd service called `fish-streaming.service`
2. Configures it to start automatically on boot
3. Starts the service immediately
4. Sets up automatic restart if the service crashes

## 🔧 Service Management Commands

### Check Service Status
```bash
sudo systemctl status fish-streaming.service
```

### View Live Logs
```bash
sudo journalctl -u fish-streaming.service -f
```

### Stop the Service
```bash
sudo systemctl stop fish-streaming.service
```

### Start the Service
```bash
sudo systemctl start fish-streaming.service
```

### Restart the Service
```bash
sudo systemctl restart fish-streaming.service
```

### Disable Auto-Start (keeps service but won't start on boot)
```bash
sudo systemctl disable fish-streaming.service
```

### Enable Auto-Start Again
```bash
sudo systemctl enable fish-streaming.service
```

### Remove Service Completely
```bash
sudo systemctl stop fish-streaming.service
sudo systemctl disable fish-streaming.service
sudo rm /etc/systemd/system/fish-streaming.service
sudo systemctl daemon-reload
```

## 📊 Monitoring

### View Last 50 Log Lines
```bash
sudo journalctl -u fish-streaming.service -n 50
```

### View Logs from Today
```bash
sudo journalctl -u fish-streaming.service --since today
```

### View Logs with Timestamps
```bash
sudo journalctl -u fish-streaming.service -o short-precise
```

## 🔍 Troubleshooting

### Service Won't Start
1. Check logs: `sudo journalctl -u fish-streaming.service -n 100`
2. Verify script exists: `ls -la /home/koi/Documents/GitHub/ishara-iot/start_streaming_server.sh`
3. Test script manually: `./start_streaming_server.sh`

### Service Crashes on Boot
- Check if Python virtual environment is properly set up
- Ensure all dependencies are installed
- Review logs for specific error messages

### Port Already in Use
- Another instance might be running
- Check: `sudo lsof -i :5000`
- Kill process: `sudo kill -9 <PID>`

## 📱 Access Points

After boot, the streaming server will be available at:

- **WebSocket Stream**: `ws://192.168.8.101:5000`
- **HTTP API**: `http://192.168.8.101:5000/api/status`
- **MJPEG Stream**: `http://192.168.8.101:5000/video_feed`
- **Test Client**: Open `web_client.html` in browser

## ⚙️ Service Configuration

The service file is located at:
- Source: `/home/koi/Documents/GitHub/ishara-iot/fish-streaming.service`
- Installed: `/etc/systemd/system/fish-streaming.service`

### Service Features:
- **Auto-restart**: Service restarts automatically if it crashes
- **10-second delay**: Waits 10 seconds between restart attempts
- **Journal logging**: All output saved to system journal
- **Network dependency**: Waits for network before starting

## 🔄 Updating the Service

If you make changes to the startup script or service file:

```bash
# After editing fish-streaming.service
sudo cp fish-streaming.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl restart fish-streaming.service
```

## ✅ Verify Auto-Start is Working

1. Run setup: `sudo ./setup_autostart.sh`
2. Reboot: `sudo reboot`
3. After reboot, check status: `sudo systemctl status fish-streaming.service`
4. Test connection: Open web browser to `http://192.168.8.101:5000/api/status`

The server should be running automatically! 🎉
