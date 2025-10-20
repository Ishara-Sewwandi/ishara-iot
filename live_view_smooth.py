#!/usr/bin/env python3
"""
OPTIMIZED Live camera view with fish detection overlay
Ultra-smooth streaming with minimal lag
"""

from camera_handler import CameraHandler
from fish_detector import FishDetector
from config import Config
import cv2
import time
from datetime import datetime
import threading
from collections import deque

class SmoothLiveView:
    def __init__(self):
        self.config = Config()
        self.camera = CameraHandler(self.config)
        self.detector = FishDetector(self.config)
        
        # Frame buffer for smooth display
        self.frame_buffer = deque(maxlen=2)
        self.detection_buffer = []
        self.running = False
        
        # Performance tracking
        self.fps = 0
        self.frame_count = 0
        
    def start(self):
        """Start the optimized live view"""
        print("╔════════════════════════════════════════════════════════╗")
        print("║     OPTIMIZED Live Fish Monitoring                    ║")
        print("║     Ultra-Smooth Streaming                            ║")
        print("╚════════════════════════════════════════════════════════╝")
        print()
        print("🎥 Starting camera...")
        
        self.camera.start()
        self.running = True
        
        # Create window with optimal settings
        cv2.namedWindow('Live Fish Monitoring - SMOOTH', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Live Fish Monitoring - SMOOTH', 1280, 720)
        
        print("✅ Camera ready!")
        print()
        print("📺 Display Controls:")
        print("  • Press 'q' - Quit")
        print("  • Press 's' - Screenshot")
        print("  • Press 'd' - Toggle detection (for max FPS)")
        print("  • Press 'f' - Toggle fullscreen")
        print()
        
        # Start detection thread (separate from display)
        detection_enabled = True
        detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
        detection_thread.start()
        
        # Main display loop (maximum speed)
        fps_time = time.time()
        fps_count = 0
        fullscreen = False
        
        try:
            while self.running:
                # Capture frame (non-blocking)
                frame = self.camera.capture_frame()
                
                if frame is None:
                    time.sleep(0.001)
                    continue
                
                self.frame_count += 1
                fps_count += 1
                
                # Calculate FPS every 30 frames
                if fps_count >= 30:
                    current_time = time.time()
                    self.fps = 30 / (current_time - fps_time)
                    fps_time = current_time
                    fps_count = 0
                
                # Draw overlays (lightweight)
                display = self._draw_lightweight_overlay(frame, detection_enabled)
                
                # Display (no processing delay)
                cv2.imshow('Live Fish Monitoring - SMOOTH', display)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    print("\n🛑 Quitting...")
                    break
                elif key == ord('s'):
                    filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    path = self.camera.save_image(display, filename)
                    print(f"📸 Screenshot saved: {path}")
                elif key == ord('d'):
                    detection_enabled = not detection_enabled
                    status = "ENABLED" if detection_enabled else "DISABLED"
                    print(f"🔍 Detection {status}")
                elif key == ord('f'):
                    fullscreen = not fullscreen
                    flag = cv2.WINDOW_FULLSCREEN if fullscreen else cv2.WINDOW_NORMAL
                    cv2.setWindowProperty('Live Fish Monitoring - SMOOTH', 
                                        cv2.WND_PROP_FULLSCREEN, flag)
        
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.running = False
            detection_thread.join(timeout=2)
            self.camera.stop()
            cv2.destroyAllWindows()
            print("✅ Camera stopped")
            print(f"📊 Final Stats: Avg FPS: {self.fps:.1f}")
    
    def _detection_loop(self):
        """Background detection thread (doesn't block display)"""
        detection_count = 0
        
        while self.running:
            try:
                # Get current frame from camera
                frame = self.camera.capture_frame()
                
                if frame is None:
                    time.sleep(0.01)
                    continue
                
                # Only detect every N frames to save CPU
                detection_count += 1
                if detection_count % self.config.SKIP_FRAMES == 0:
                    detections = self.detector.detect(frame)
                    self.detection_buffer = detections
                
                # Small sleep to not overload CPU
                time.sleep(0.05)
                
            except Exception as e:
                print(f"⚠️  Detection error: {e}")
                time.sleep(0.1)
    
    def _draw_lightweight_overlay(self, frame, detection_enabled):
        """Draw minimal overlays for maximum performance"""
        h, w = frame.shape[:2]
        
        # Info panel (small and efficient)
        cv2.rectangle(frame, (0, 0), (350, 120), (0, 0, 0), -1)
        
        # FPS (most important metric)
        fps_color = (0, 255, 0) if self.fps >= 25 else (0, 200, 255) if self.fps >= 15 else (0, 0, 255)
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, fps_color, 2)
        
        # Fish count
        if detection_enabled and self.detection_buffer:
            cv2.putText(frame, f"Fish: {len(self.detection_buffer)}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Draw simple boxes (no labels for speed)
            for det in self.detection_buffer:
                x1, y1, x2, y2 = det['bbox']
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Detection: OFF", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 2)
        
        # Frame count
        cv2.putText(frame, f"Frame: {self.frame_count}", (10, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Status
        status = "SMOOTH" if self.fps >= 25 else "GOOD" if self.fps >= 15 else "SLOW"
        status_color = (0, 255, 0) if self.fps >= 25 else (0, 200, 255) if self.fps >= 15 else (0, 0, 255)
        cv2.putText(frame, status, (w - 100, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        
        return frame

def main():
    viewer = SmoothLiveView()
    viewer.start()

if __name__ == "__main__":
    main()
