#!/usr/bin/env python3
"""
Test script for camera functionality
"""

from camera_handler import CameraHandler
from config import Config
import cv2
import time

def main():
    print("Testing Pi Camera Module 2...")
    
    config = Config()
    camera = CameraHandler(config)
    
    try:
        # Start camera
        camera.start()
        print("Camera started successfully")
        
        # Capture and display frames
        for i in range(10):
            frame = camera.capture_frame()
            
            if frame is not None:
                print(f"Frame {i+1}: {frame.shape}")
                
                # Save test image
                if i == 5:
                    path = camera.save_image(frame, "test_capture.jpg")
                    print(f"Test image saved: {path}")
            else:
                print(f"Frame {i+1}: Failed to capture")
            
            time.sleep(0.5)
        
        print("\nCamera test completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        camera.stop()

if __name__ == "__main__":
    main()
