#!/usr/bin/env python3
"""
Test script for fish detection
"""

from camera_handler import CameraHandler
from fish_detector import FishDetector
from config import Config
import cv2
import time

def main():
    print("Testing Fish Detection...")
    
    config = Config()
    camera = CameraHandler(config)
    detector = FishDetector(config)
    
    try:
        camera.start()
        print("Camera started")
        
        # Capture and detect
        for i in range(20):
            frame = camera.capture_frame()
            
            if frame is not None:
                # Detect fish
                detections = detector.detect(frame)
                
                print(f"Frame {i+1}: {len(detections)} fish detected")
                
                if detections:
                    # Draw detections
                    frame_with_boxes = detector.draw_detections(frame, detections)
                    
                    # Save annotated image
                    if i % 5 == 0:
                        cv2.imwrite(f"detection_test_{i}.jpg", frame_with_boxes)
                        print(f"  Saved annotated image: detection_test_{i}.jpg")
            
            time.sleep(0.5)
        
        print("\nDetection test completed!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        camera.stop()

if __name__ == "__main__":
    main()
