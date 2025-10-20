#!/usr/bin/env python3
"""
Fish Mortality Detection System for Raspberry Pi 4
Main orchestration module
"""

import threading
import time
from datetime import datetime
from camera_handler import CameraHandler
from fish_detector import FishDetector
from behavior_analyzer import BehaviorAnalyzer
from rainfall_detector import RainfallDetector
from alert_system import AlertSystem
from config import Config
import logging
import cv2
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fish_monitoring.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class FishMonitoringSystem:
    def __init__(self):
        """Initialize the fish monitoring system"""
        logger.info("Initializing Fish Monitoring System...")
        
        self.config = Config()
        self.camera = CameraHandler(self.config)
        self.fish_detector = FishDetector(self.config)
        self.behavior_analyzer = BehaviorAnalyzer(self.config)
        self.rainfall_detector = RainfallDetector(self.config)
        self.alert_system = AlertSystem(self.config)
        
        self.running = False
        self.monitoring_thread = None
        self.rainfall_thread = None
        
        logger.info("System initialized successfully")
    
    def start(self):
        """Start the monitoring system"""
        logger.info("Starting monitoring system...")
        self.running = True
        
        # Start camera
        self.camera.start()
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitor_fish)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        # Start rainfall detection thread
        self.rainfall_thread = threading.Thread(target=self._monitor_rainfall)
        self.rainfall_thread.daemon = True
        self.rainfall_thread.start()
        
        logger.info("Monitoring system started")
    
    def stop(self):
        """Stop the monitoring system"""
        logger.info("Stopping monitoring system...")
        self.running = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        if self.rainfall_thread:
            self.rainfall_thread.join(timeout=5)
        
        self.camera.stop()
        logger.info("Monitoring system stopped")
    
    def _monitor_fish(self):
        """Main fish monitoring loop - 25 FPS Default Mode"""
        frame_count = 0
        detection_count = 0
        last_detections = []
        last_analysis = {}
        
        # Create display window if enabled
        if self.config.DISPLAY_ENABLED:
            cv2.namedWindow('Fish Mortality Detection - 25 FPS', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Fish Mortality Detection - 25 FPS', 
                           self.config.DISPLAY_WIDTH, self.config.DISPLAY_HEIGHT)
        
        # FPS tracking
        fps_start_time = time.time()
        fps_frame_count = 0
        current_fps = 0
        target_frame_time = 1.0 / 25.0  # Target 25 FPS
        
        # Detection FPS tracking
        detection_fps = 0.0
        detection_fps_count = 0
        detection_fps_start = time.time()
        
        logger.info("Starting 25 FPS fish mortality detection mode")
        logger.info(f"Detection interval: every {self.config.SKIP_FRAMES} frames")
        logger.info(f"YOLO image size: {self.config.YOLO_IMG_SIZE}x{self.config.YOLO_IMG_SIZE}")
        
        while self.running:
            try:
                loop_start = time.time()
                
                # Capture frame
                frame = self.camera.capture_frame()
                if frame is None:
                    time.sleep(0.01)
                    continue
                
                frame_count += 1
                fps_frame_count += 1
                
                # Calculate FPS
                if fps_frame_count % 25 == 0:
                    fps_end_time = time.time()
                    current_fps = 25 / (fps_end_time - fps_start_time)
                    fps_start_time = fps_end_time
                
                # 25 FPS Mode: Display every frame, detect every Nth frame
                display_frame = frame.copy()
                
                # Only run detection every SKIP_FRAMES frames
                if frame_count % self.config.SKIP_FRAMES == 0:
                    detection_start = time.time()
                    
                    detection_count += 1
                    detection_fps_count += 1
                    
                    # Detect fish using YOLOv8
                    detections = self.fish_detector.detect(frame)
                    last_detections = detections
                    
                    analysis_results = {}
                    if detections:
                        # Analyze behavior
                        analysis_results = self.behavior_analyzer.analyze(
                            frame, 
                            detections,
                            detection_count
                        )
                        last_analysis = analysis_results
                        
                        # Check for mortality indicators
                        for fish_id, behavior in analysis_results.items():
                            if self._is_mortality_detected(behavior):
                                logger.warning(f"Mortality indicators detected for fish {fish_id}")
                                
                                # Save and alert in background thread (non-blocking)
                                threading.Thread(target=self._save_and_alert, 
                                               args=(frame.copy(), fish_id, behavior)).start()
                    
                    # Update detection FPS every 10 detections
                    if detection_fps_count >= 10:
                        detection_elapsed = time.time() - detection_fps_start
                        detection_fps = detection_fps_count / detection_elapsed
                        detection_fps_count = 0
                        detection_fps_start = time.time()
                
                # Display with last known detections (smooth 25 FPS)
                if self.config.DISPLAY_ENABLED:
                    display_frame = self._draw_display(display_frame, last_detections, 
                                                      last_analysis, frame_count, current_fps, detection_fps)
                    cv2.imshow('Fish Mortality Detection - 25 FPS', display_frame)
                    
                    # Non-blocking key check
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        logger.info("Quit key pressed")
                        self.running = False
                        break
                
                # Frame pacing for stable 25 FPS
                elapsed = time.time() - loop_start
                if elapsed < target_frame_time:
                    time.sleep(target_frame_time - elapsed)
                
            except Exception as e:
                logger.error(f"Error in fish monitoring loop: {e}", exc_info=True)
                time.sleep(0.1)
        
        # Cleanup display
        if self.config.DISPLAY_ENABLED:
            cv2.destroyAllWindows()
    
    def _save_and_alert(self, frame, fish_id, behavior):
        """Save image and send alert in separate thread"""
        try:
            image_path = self.camera.save_image(
                frame, 
                f"mortality_alert_{fish_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            )
            
            self.alert_system.send_mortality_alert(
                fish_id=fish_id,
                behavior=behavior,
                image_path=image_path,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error in save_and_alert: {e}")
    
    def _monitor_rainfall(self):
        """Rainfall monitoring loop"""
        while self.running:
            try:
                # Check for rainfall
                rainfall_detected = self.rainfall_detector.detect()
                
                if rainfall_detected:
                    logger.warning("Rainfall detected!")
                    
                    # Capture current frame as evidence
                    frame = self.camera.capture_frame()
                    if frame is not None:
                        image_path = self.camera.save_image(
                            frame,
                            f"rainfall_alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                        )
                    else:
                        image_path = None
                    
                    # Send rainfall alert
                    self.alert_system.send_rainfall_alert(
                        intensity=self.rainfall_detector.get_intensity(),
                        image_path=image_path,
                        timestamp=datetime.now()
                    )
                    
                    # Wait before next check (avoid spam)
                    time.sleep(self.config.RAINFALL_ALERT_COOLDOWN)
                else:
                    time.sleep(self.config.RAINFALL_CHECK_INTERVAL)
                    
            except Exception as e:
                logger.error(f"Error in rainfall monitoring loop: {e}", exc_info=True)
                time.sleep(5)
    
    def _is_mortality_detected(self, behavior):
        """
        Determine if mortality indicators are present
        
        Args:
            behavior (dict): Behavior analysis results
            
        Returns:
            bool: True if mortality indicators detected
        """
        indicators = 0
        
        # Check for fin inactivity
        if behavior.get('fin_activity', 1.0) < self.config.FIN_ACTIVITY_THRESHOLD:
            indicators += 1
        
        # Check for side floating
        if behavior.get('is_side_floating', False):
            indicators += 1
        
        # Check for minimal movement
        if behavior.get('movement_score', 1.0) < self.config.MOVEMENT_THRESHOLD:
            indicators += 1
        
        # Require multiple indicators for alert
        return indicators >= 2
    
    def _draw_display(self, frame, detections, analysis_results, frame_count, fps=0, detection_fps=0):
        """
        Draw visual overlays on the display frame - 25 FPS Optimized
        
        Args:
            frame: Input frame
            detections: Fish detections
            analysis_results: Behavior analysis results
            frame_count: Current frame number
            fps: Current display FPS
            detection_fps: Current detection FPS
            
        Returns:
            Annotated frame
        """
        display = frame
        h, w = display.shape[:2]
        
        # Minimal overlay for performance
        overlay = display.copy()
        cv2.rectangle(overlay, (0, 0), (450, 170), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, display, 0.3, 0, display)
        
        # Header - 25 FPS Mode indicator
        cv2.putText(display, "Fish Mortality Detection - 25 FPS", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Display FPS with color indicator (25 FPS target)
        fps_color = (0, 255, 0) if fps >= 24 else (0, 200, 255) if fps >= 22 else (0, 0, 255)
        cv2.putText(display, f"Display: {fps:.1f} / 25 FPS", (10, 65),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, fps_color, 2)
        
        # Detection FPS with color indicator
        det_color = (0, 255, 0) if detection_fps >= 4 else (0, 200, 255) if detection_fps >= 3 else (0, 0, 255)
        cv2.putText(display, f"Detection: {detection_fps:.1f} FPS", (10, 95),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, det_color, 1)
        
        # Fish count
        cv2.putText(display, f"Fish Detected: {len(detections)}", (10, 125),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Status
        cv2.putText(display, "Press 'q' to quit", (10, 155),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 255), 1)
        
        # Draw fish detections and behavior info
        for detection in detections:
            bbox = detection['bbox']
            x1, y1, x2, y2 = bbox
            confidence = detection['confidence']
            
            # Find corresponding analysis
            fish_id = None
            behavior = None
            for fid, analysis in analysis_results.items():
                if analysis.get('bbox') == bbox:
                    fish_id = fid
                    behavior = analysis
                    break
            
            # Determine box color based on health status
            if behavior:
                mortality_detected = self._is_mortality_detected(behavior)
                color = (0, 0, 255) if mortality_detected else (0, 255, 0)  # Red or Green
                thickness = 3 if mortality_detected else 2
            else:
                color = (255, 255, 0)  # Yellow for no analysis yet
                thickness = 2
            
            # Draw bounding box
            cv2.rectangle(display, (x1, y1), (x2, y2), color, thickness)
            
            # Draw fish ID
            if fish_id is not None:
                label = f"Fish #{fish_id}"
                cv2.putText(display, label, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Draw behavior metrics if available
            if behavior:
                info_y = y2 + 20
                
                # Fin activity
                fin_activity = behavior.get('fin_activity', 0)
                fin_color = (0, 255, 0) if fin_activity > self.config.FIN_ACTIVITY_THRESHOLD else (0, 0, 255)
                cv2.putText(display, f"Fin: {fin_activity:.0%}", (x1, info_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, fin_color, 1)
                
                # Movement
                movement = behavior.get('movement_score', 0)
                move_color = (0, 255, 0) if movement > self.config.MOVEMENT_THRESHOLD else (0, 0, 255)
                cv2.putText(display, f"Move: {movement:.0%}", (x1, info_y + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, move_color, 1)
                
                # Side floating warning
                if behavior.get('is_side_floating', False):
                    cv2.putText(display, "SIDE FLOATING!", (x1, info_y + 40),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        # Draw status indicators
        status_y = h - 30
        
        # System status
        cv2.putText(display, "SYSTEM: ACTIVE", (w - 200, status_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return display


def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("Fish Mortality Detection System")
    logger.info("Raspberry Pi 4 + Pi Camera Module 2")
    logger.info("=" * 60)
    
    system = FishMonitoringSystem()
    
    try:
        system.start()
        logger.info("System running. Press Ctrl+C to stop.")
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutdown signal received")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        system.stop()
        logger.info("System shutdown complete")


if __name__ == "__main__":
    main()
