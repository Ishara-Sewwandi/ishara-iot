#!/bin/bash
# Complete setup and usage guide for Fish Mortality Detection System

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     Fish Mortality Detection System - Complete Guide          ║"
echo "║           Raspberry Pi 4 + Pi Camera Module 2                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

show_menu() {
    echo "Select an option:"
    echo ""
    echo "  1) Run ULTRA-SMOOTH LIVE VIEW ⚡ (25-30 FPS, recommended)"
    echo "  2) Run FULL MONITORING with display (smooth mode)"
    echo "  3) Run STANDARD live view (testing)"
    echo "  4) Run HEADLESS mode (no display)"
    echo "  5) Test camera"
    echo "  6) Test fish detection"
    echo "  7) Test alerts"
    echo "  8) View live logs"
    echo "  9) Configuration"
    echo "  h) Help & Documentation"
    echo "  0) Exit"
    echo ""
    read -p "Enter choice [0-9/h]: " choice
    
    case $choice in
        1) run_smooth_view ;;
        2) run_live_display ;;
        3) run_live_view ;;
        4) run_headless ;;
        5) test_camera ;;
        6) test_detector ;;
        7) test_alerts ;;
        8) view_logs ;;
        9) show_config ;;
        h|H) show_help ;;
        0) exit 0 ;;
        *) echo "Invalid option"; show_menu ;;
    esac
}

run_smooth_view() {
    echo ""
    echo "⚡ Starting ULTRA-SMOOTH LIVE VIEW..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎯 OPTIMIZED FOR MAXIMUM PERFORMANCE"
    echo ""
    echo "Expected FPS: 25-30 (butter smooth!)"
    echo ""
    echo "Features:"
    echo "  ✅ Ultra-smooth streaming"
    echo "  ✅ Real-time fish detection"
    echo "  ✅ Performance monitoring"
    echo "  ✅ Interactive controls"
    echo ""
    echo "Controls:"
    echo "  • Press 'q' to quit"
    echo "  • Press 's' to save screenshot"
    echo "  • Press 'd' to toggle detection (max FPS)"
    echo "  • Press 'f' for fullscreen"
    echo ""
    echo "Display shows:"
    echo "  🟢 25-30 FPS = Excellent (smooth)"
    echo "  🟡 15-24 FPS = Good"
    echo "  🔴 < 15 FPS = Needs optimization"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    read -p "Press Enter to start (or Ctrl+C to cancel)..."
    
    export DISPLAY=:0
    source venv/bin/activate
    export PYTHONPATH=/usr/lib/python3/dist-packages:$PYTHONPATH
    python3 live_view_smooth.py
}

run_live_display() {
    echo ""
    echo "🎥 Starting Fish Monitoring System with LIVE DISPLAY..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Features:"
    echo "  • Real-time camera feed with overlays"
    echo "  • Fish detection and tracking"
    echo "  • Behavior analysis (fin activity, movement, side-floating)"
    echo "  • Rainfall detection"
    echo "  • Automatic alerts"
    echo ""
    echo "Controls:"
    echo "  • Press 'q' to quit"
    echo ""
    echo "Display Indicators:"
    echo "  🟢 Green box  = Healthy fish"
    echo "  🔴 Red box    = Mortality signs detected"
    echo "  🟡 Yellow box = Analyzing..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    read -p "Press Enter to start (or Ctrl+C to cancel)..."
    
    export DISPLAY=:0
    ./start.sh
}

run_live_view() {
    echo ""
    echo "📹 Starting LIVE VIEW ONLY (testing mode)..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "This mode shows camera feed + fish detection only."
    echo "No behavior monitoring or alerts."
    echo ""
    echo "Controls:"
    echo "  • Press 'q' to quit"
    echo "  • Press 's' to save screenshot"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    read -p "Press Enter to start (or Ctrl+C to cancel)..."
    
    export DISPLAY=:0
    source venv/bin/activate
    export PYTHONPATH=/usr/lib/python3/dist-packages:$PYTHONPATH
    python3 live_view.py
}

run_headless() {
    echo ""
    echo "🖥️  Starting in HEADLESS mode (no display)..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "System will run in background without visual display."
    echo "Perfect for remote/server deployment."
    echo ""
    echo "To view activity:"
    echo "  tail -f fish_monitoring.log"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Temporarily disable display
    sed -i 's/DISPLAY_ENABLED = True/DISPLAY_ENABLED = False/' config.py
    
    read -p "Press Enter to start (or Ctrl+C to cancel)..."
    ./start.sh
    
    # Re-enable display
    sed -i 's/DISPLAY_ENABLED = False/DISPLAY_ENABLED = True/' config.py
}

test_camera() {
    echo ""
    echo "📷 Testing camera..."
    source venv/bin/activate
    export PYTHONPATH=/usr/lib/python3/dist-packages:$PYTHONPATH
    python3 test_camera.py
    echo ""
    read -p "Press Enter to continue..."
    show_menu
}

test_detector() {
    echo ""
    echo "🔍 Testing fish detector..."
    source venv/bin/activate
    export PYTHONPATH=/usr/lib/python3/dist-packages:$PYTHONPATH
    python3 test_detector.py
    echo ""
    read -p "Press Enter to continue..."
    show_menu
}

test_alerts() {
    echo ""
    echo "🚨 Testing alert system..."
    source venv/bin/activate
    export PYTHONPATH=/usr/lib/python3/dist-packages:$PYTHONPATH
    python3 test_alerts.py
    echo ""
    read -p "Press Enter to continue..."
    show_menu
}

view_logs() {
    echo ""
    echo "📋 Viewing live logs (Ctrl+C to stop)..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    tail -f fish_monitoring.log
}

show_config() {
    echo ""
    echo "⚙️  Configuration Files:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "1. config.py - Main configuration"
    echo "   • Camera settings (resolution, FPS)"
    echo "   • Display settings (enable/disable, size)"
    echo "   • Detection thresholds"
    echo "   • Alert intervals"
    echo ""
    echo "2. .env - Credentials (create if not exists)"
    echo "   • Telegram bot token and chat ID"
    echo "   • Webhook URL"
    echo "   • Email settings"
    echo ""
    echo "Quick edits:"
    echo "  nano config.py"
    echo "  nano .env"
    echo ""
    read -p "Press Enter to continue..."
    show_menu
}

show_help() {
    echo ""
    echo "📚 Help & Documentation:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Documentation Files:"
    echo "  • README.md              - Complete system overview"
    echo "  • DISPLAY_GUIDE.md       - Live display documentation"
    echo "  • QUICKSTART_DISPLAY.md  - Quick start guide"
    echo ""
    echo "Key Features:"
    echo ""
    echo "🐟 Fish Mortality Detection:"
    echo "   • YOLOv8-based fish detection"
    echo "   • Fin activity monitoring (optical flow)"
    echo "   • Side-floating detection"
    echo "   • Movement analysis"
    echo ""
    echo "🌧️ Rainfall Detection:"
    echo "   • Hardware sensor (GPIO)"
    echo "   • Visual detection (camera-based)"
    echo "   • Immediate farmer alerts"
    echo ""
    echo "🚨 Alert System:"
    echo "   • Telegram notifications with images"
    echo "   • Email alerts"
    echo "   • Webhook integration"
    echo ""
    echo "📺 Live Display:"
    echo "   • Real-time camera feed"
    echo "   • Fish detection overlays"
    echo "   • Behavior metrics"
    echo "   • Color-coded health indicators"
    echo ""
    echo "System Requirements:"
    echo "  • Raspberry Pi 4 Model B"
    echo "  • Pi Camera Module 2"
    echo "  • Python 3.9+"
    echo "  • 2GB+ RAM recommended"
    echo ""
    echo "Common Commands:"
    echo "  ./start.sh              - Start with display"
    echo "  python3 live_view.py    - View only"
    echo "  tail -f *.log           - View logs"
    echo "  htop                    - Monitor resources"
    echo ""
    echo "Troubleshooting:"
    echo "  • Camera not working → sudo raspi-config → Enable camera → Reboot"
    echo "  • Display not showing → export DISPLAY=:0"
    echo "  • Low FPS → Lower resolution in config.py"
    echo "  • Import errors → Check venv: source venv/bin/activate"
    echo ""
    read -p "Press Enter to continue..."
    show_menu
}

# Main execution
cd "$(dirname "$0")"
show_menu
