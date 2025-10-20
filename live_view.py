#!/usr/bin/env python3
"""
Live camera view with fish detection overlay
Standalone script for testing and viewing
"""

from camera_handler import CameraHandler
from fish_detector import FishDetector
from config import Config
import cv2
import time
from datetime import datetime

def main():
    print("Starting Live Camera Feed...")
    print("Press 'q' to quit")
    print("Press 's' to save screenshot")
    
    config = Config()
    camera = CameraHandler(config)
    detector = FishDetector(config)
    
    try:
        camera.start()
        
        # Create window
        cv2.namedWindow('Live Fish Monitoring', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Live Fish Monitoring', 1280, 720)
        
        frame_count = 0
        fps_time = time.time()
        fps = 0
        
        while True:
            frame = camera.capture_frame()
            
            if frame is None:
                time.sleep(0.1)
                continue
            
            frame_count += 1
            
            # Detect fish
            detections = detector.detect(frame)
            
            # Draw detections
            display = detector.draw_detections(frame, detections)
            
            # Calculate FPS
            if frame_count % 10 == 0:
                current_time = time.time()
                fps = 10 / (current_time - fps_time)
                fps_time = current_time
            
            # Add info overlay
            h, w = display.shape[:2]
            
            # Info panel
            cv2.rectangle(display, (0, 0), (350, 100), (0, 0, 0), -1)
            cv2.putText(display, "Live Fish Monitoring", (10, 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(display, f"FPS: {fps:.1f}", (10, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(display, f"Fish: {len(detections)}", (10, 75),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Controls
            cv2.putText(display, "Q: Quit | S: Screenshot", (10, h - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            
            # Display
            cv2.imshow('Live Fish Monitoring', display)
            
            # Handle keys
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("Quitting...")
                break
            elif key == ord('s'):
                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                path = camera.save_image(display, filename)
                print(f"Screenshot saved: {path}")
            
            time.sleep(0.01)
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        camera.stop()
        cv2.destroyAllWindows()
        print("Camera stopped")

if __name__ == "__main__":
    main()
