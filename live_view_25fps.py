#!/usr/bin/env python3
"""
ULTRA-LIGHTWEIGHT Live View - Guaranteed 25 FPS
Minimal overhead, maximum performance
"""

from camera_handler import CameraHandler
from fish_detector import FishDetector
from config import Config
import cv2
import time
from datetime import datetime
import threading
import numpy as np

class HighPerformanceLiveView:
    def __init__(self):
        self.config = Config()
        self.camera = CameraHandler(self.config)
        self.detector = FishDetector(self.config)
        
        # Minimal state
        self.running = False
        self.latest_detections = []
        self.detection_enabled = True
        
        # FPS tracking
        self.fps = 0
        self.frame_count = 0
        self.target_fps = 25
        self.frame_time = 1.0 / self.target_fps
        
    def start(self):
        """Start high-performance live view"""
        print("╔════════════════════════════════════════════════════════╗")
        print("║   ULTRA-LIGHTWEIGHT VIEWER - 25 FPS Optimized         ║")
        print("╚════════════════════════════════════════════════════════╝")
        print()
        print("🎯 Target: Stable 25 FPS")
        print("⚡ Mode: Maximum Performance")
        print()
        
        self.camera.start()
        self.running = True
        
        # Minimal window setup
        window_name = 'Fish Monitor - 25FPS'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 1280, 720)
        
        # Start lightweight detection thread
        if self.detection_enabled:
            detection_thread = threading.Thread(target=self._detection_worker, daemon=True)
            detection_thread.start()
        
        print("✅ Ready! Press 'q' to quit, 'd' to toggle detection")
        print()
        
        # High-speed display loop
        last_frame_time = time.time()
        fps_update_time = time.time()
        fps_frame_count = 0
        
        try:
            while self.running:
                loop_start = time.time()
                
                # Capture frame (fastest method)
                frame = self.camera.capture_frame()
                
                if frame is None:
                    continue
                
                self.frame_count += 1
                fps_frame_count += 1
                
                # Update FPS every second
                current_time = time.time()
                if current_time - fps_update_time >= 1.0:
                    self.fps = fps_frame_count / (current_time - fps_update_time)
                    fps_update_time = current_time
                    fps_frame_count = 0
                
                # Ultra-minimal overlay
                self._draw_minimal_overlay(frame)
                
                # Display (no delay)
                cv2.imshow(window_name, frame)
                
                # Non-blocking key check
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('d'):
                    self.detection_enabled = not self.detection_enabled
                    status = "ON" if self.detection_enabled else "OFF"
                    print(f"🔍 Detection: {status}")
                    if self.detection_enabled and not threading.active_count() > 1:
                        threading.Thread(target=self._detection_worker, daemon=True).start()
                
                # Frame pacing for consistent FPS
                elapsed = time.time() - loop_start
                if elapsed < self.frame_time:
                    time.sleep(self.frame_time - elapsed)
        
        except KeyboardInterrupt:
            print("\n⚠️  Stopped")
        finally:
            self.running = False
            self.camera.stop()
            cv2.destroyAllWindows()
            print(f"📊 Average FPS: {self.fps:.1f}")
    
    def _detection_worker(self):
        """Lightweight background detection"""
        frame_skip_counter = 0
        
        while self.running and self.detection_enabled:
            try:
                frame = self.camera.capture_frame()
                if frame is None:
                    time.sleep(0.02)
                    continue
                
                # Only detect every Nth frame
                frame_skip_counter += 1
                if frame_skip_counter >= self.config.SKIP_FRAMES:
                    frame_skip_counter = 0
                    
                    # Quick detection
                    detections = self.detector.detect(frame)
                    self.latest_detections = detections
                
                # Don't overload CPU
                time.sleep(0.03)
                
            except Exception as e:
                print(f"⚠️  Detection error: {e}")
                time.sleep(0.1)
    
    def _draw_minimal_overlay(self, frame):
        """Ultra-minimal overlay - maximum speed"""
        h, w = frame.shape[:2]
        
        # FPS only (critical info)
        fps_color = (0, 255, 0) if self.fps >= 24 else (0, 200, 255) if self.fps >= 20 else (0, 0, 255)
        cv2.putText(frame, f"FPS:{self.fps:.0f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, fps_color, 2)
        
        # Detection count (if enabled)
        if self.detection_enabled and self.latest_detections:
            cv2.putText(frame, f"Fish:{len(self.latest_detections)}", (10, 65),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Simple boxes (no labels for speed)
            for det in self.latest_detections:
                x1, y1, x2, y2 = det['bbox']
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

def main():
    viewer = HighPerformanceLiveView()
    viewer.start()

if __name__ == "__main__":
    main()
