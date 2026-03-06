#!/bin/bash
# LiveKit Service Status Checker

echo "========================================="
echo "   LiveKit Auto-Start Configuration"
echo "========================================="
echo ""

# Check service status
echo "📋 Service Status:"
echo "-------------------"
systemctl is-enabled livekit-publisher.service 2>/dev/null && echo "✅ livekit-publisher: ENABLED (will start on boot)" || echo "❌ livekit-publisher: DISABLED"
systemctl is-active livekit-publisher.service 2>/dev/null && echo "✅ livekit-publisher: RUNNING" || echo "❌ livekit-publisher: STOPPED"
echo ""

systemctl is-enabled fish-streaming.service 2>/dev/null && echo "⚠️  fish-streaming: ENABLED" || echo "✅ fish-streaming: DISABLED (correct)"
systemctl is-active fish-streaming.service 2>/dev/null && echo "⚠️  fish-streaming: RUNNING" || echo "✅ fish-streaming: STOPPED (correct)"
echo ""

# Check environment configuration
echo "🔧 LiveKit Configuration:"
echo "-------------------------"
if [ -f .env ]; then
    source .env
    echo "LiveKit URL: ${LIVEKIT_URL}"
    echo "Room: ${LIVEKIT_ROOM}"
    echo "API Key: ${LIVEKIT_API_KEY:0:10}..."
else
    echo "❌ .env file not found"
fi
echo ""

# Check recent logs
echo "📝 Recent Connection Attempts:"
echo "------------------------------"
sudo journalctl -u livekit-publisher.service --since "2 minutes ago" --no-pager | grep -E "(Connected|Failed|ERROR|Connecting to LiveKit)" | tail -5
echo ""

# Check certificate issue
echo "🔐 SSL Certificate Status:"
echo "--------------------------"
if sudo journalctl -u livekit-publisher.service --since "2 minutes ago" --no-pager | grep -q "NotValidForName"; then
    echo "❌ Certificate Error: NotValidForName"
    echo "   Problem: Traefik is using self-signed certificate"
    echo "   Solution: Configure Let's Encrypt on VPS (see VPS_TRAEFIK_LETSENCRYPT_CONFIG.md)"
elif sudo journalctl -u livekit-publisher.service --since "2 minutes ago" --no-pager | grep -q "UnknownIssuer"; then
    echo "❌ Certificate Error: UnknownIssuer"
    echo "   Problem: Certificate not trusted"
elif sudo journalctl -u livekit-publisher.service --since "2 minutes ago" --no-pager | grep -q "Connected to LiveKit"; then
    echo "✅ Connected successfully"
else
    echo "⏳ Connecting..."
fi
echo ""

echo "========================================="
echo "Commands:"
echo "  View live logs: sudo journalctl -u livekit-publisher.service -f"
echo "  Restart service: sudo systemctl restart livekit-publisher.service"
echo "  Stop service: sudo systemctl stop livekit-publisher.service"
echo "  Check configuration: cat .env"
echo "========================================="
