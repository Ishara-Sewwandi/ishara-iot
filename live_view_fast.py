#!/usr/bin/env python3
"""
Ultra-Fast Live View - Maximum FPS Mode
Simplified detection without behavior analysis for maximum speed
"""

import cv2
import time
import logging
from camera_handler import CameraHandler
from fish_detector import FishDetector
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Ultra-fast live view with basic fish detection only"""
    config = Config()
    
    # Override for maximum speed
    config.SKIP_FRAMES = 10  # Detect every 10th frame
    config.YOLO_IMG_SIZE = 320  # Smallest size
    config.CAMERA_WIDTH = 960
    config.CAMERA_HEIGHT = 540
    
    logger.info("=" * 60)
    logger.info("ULTRA-FAST MODE - Maximum FPS Fish Detection")
    logger.info("=" * 60)
    logger.info(f"Camera: {config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT} @ {config.FRAME_RATE}fps")
    logger.info(f"YOLO: {config.YOLO_IMG_SIZE}x{config.YOLO_IMG_SIZE}")
    logger.info(f"Detection: Every {config.SKIP_FRAMES} frames")
    logger.info("Behavior Analysis: DISABLED (detection only)")
    logger.info("=" * 60)
    
    # Initialize
    camera = CameraHandler(config)
    detector = FishDetector(config)
    
    camera.start()
    
    # Create window
    cv2.namedWindow('Fast Detection Mode', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Fast Detection Mode', config.CAMERA_WIDTH, config.CAMERA_HEIGHT)
    
    # Tracking
    frame_count = 0
    last_detections = []
    
    # FPS tracking
    fps_counter = 0
    fps_start = time.time()
    current_fps = 0
    
    # Detection FPS
    det_counter = 0
    det_start = time.time()
    det_fps = 0
    
    # Frame pacing
    target_frame_time = 1.0 / 25.0
    
    logger.info("Starting ultra-fast mode... Press 'q' to quit")
    
    try:
        while True:
            loop_start = time.time()
            
            # Capture frame
            frame = camera.capture_frame()
            if frame is None:
                time.sleep(0.01)
                continue
            
            frame_count += 1
            fps_counter += 1
            
            # Calculate display FPS
            if fps_counter >= 25:
                fps_elapsed = time.time() - fps_start
                current_fps = fps_counter / fps_elapsed
                fps_counter = 0
                fps_start = time.time()
            
            # Detection (minimal processing)
            if frame_count % config.SKIP_FRAMES == 0:
                det_start_time = time.time()
                
                detections = detector.detect(frame)
                last_detections = detections
                
                det_counter += 1
                if det_counter >= 5:
                    det_elapsed = time.time() - det_start
                    det_fps = det_counter / det_elapsed
                    det_counter = 0
                    det_start = time.time()
                
                det_time = (time.time() - det_start_time) * 1000
                logger.debug(f"Detection: {len(detections)} fish in {det_time:.1f}ms")
            
            # Ultra-minimal display overlay
            display = frame.copy()
            
            # Tiny info box
            cv2.rectangle(display, (5, 5), (320, 110), (0, 0, 0), -1)
            cv2.rectangle(display, (5, 5), (320, 110), (0, 255, 255), 2)
            
            # Title
            cv2.putText(display, "ULTRA-FAST MODE", (15, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            # Display FPS (should be ~25)
            fps_color = (0, 255, 0) if current_fps >= 24 else (0, 200, 255) if current_fps >= 22 else (0, 0, 255)
            cv2.putText(display, f"Display: {current_fps:.1f} FPS", (15, 55),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, fps_color, 1)
            
            # Detection FPS
            det_color = (0, 255, 0) if det_fps >= 2 else (0, 200, 255) if det_fps >= 1.5 else (0, 0, 255)
            cv2.putText(display, f"Detect: {det_fps:.1f} FPS", (15, 75),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, det_color, 1)
            
            # Fish count
            cv2.putText(display, f"Fish: {len(last_detections)}", (15, 95),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Draw simple bounding boxes (no labels)
            for det in last_detections:
                x1, y1, x2, y2 = det['bbox']
                cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Show
            cv2.imshow('Fast Detection Mode', display)
            
            # Key check
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            # Frame pacing
            elapsed = time.time() - loop_start
            if elapsed < target_frame_time:
                time.sleep(target_frame_time - elapsed)
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    
    finally:
        camera.stop()
        cv2.destroyAllWindows()
        logger.info("Ultra-fast mode stopped")


if __name__ == "__main__":
    main()
