#!/usr/bin/env python3
"""
Test script for alert system
"""

from alert_system import AlertSystem
from config import Config
from datetime import datetime
import os

def main():
    print("Testing Alert System...")
    
    config = Config()
    alerts = AlertSystem(config)
    
    # Test mortality alert
    print("\n1. Testing mortality alert...")
    behavior = {
        'fin_activity': 0.15,
        'is_side_floating': True,
        'movement_score': 0.10
    }
    
    # Create a dummy image for testing
    test_image = None
    if os.path.exists("alerts/images"):
        images = [f for f in os.listdir("alerts/images") if f.endswith('.jpg')]
        if images:
            test_image = os.path.join("alerts/images", images[0])
    
    alerts.send_mortality_alert(
        fish_id=1,
        behavior=behavior,
        image_path=test_image,
        timestamp=datetime.now()
    )
    
    print("Mortality alert sent (check your configured channels)")
    
    # Test rainfall alert
    print("\n2. Testing rainfall alert...")
    alerts.send_rainfall_alert(
        intensity='moderate',
        image_path=test_image,
        timestamp=datetime.now()
    )
    
    print("Rainfall alert sent (check your configured channels)")
    
    print("\n✓ Alert test completed!")
    print("\nNote: Make sure you have configured:")
    print("- Telegram bot token and chat ID")
    print("- Webhook URL")
    print("- Email credentials (if enabled)")

if __name__ == "__main__":
    main()
