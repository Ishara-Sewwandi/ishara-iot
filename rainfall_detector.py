#!/usr/bin/env python3
"""
Rainfall Detection Module
Detects rainfall using sensor and/or visual analysis
"""

import cv2
import numpy as np
import logging
import time

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    logging.warning("RPi.GPIO not available. Hardware sensor disabled.")

logger = logging.getLogger(__name__)


class RainfallDetector:
    def __init__(self, config):
        """Initialize rainfall detector"""
        self.config = config
        self.sensor_available = False
        self.last_detection_time = 0
        self.detection_count = 0
        
        # Setup GPIO sensor if available
        if GPIO_AVAILABLE and hasattr(config, 'RAINFALL_SENSOR_PIN'):
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(config.RAINFALL_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                self.sensor_available = True
                logger.info(f"Rainfall sensor initialized on GPIO pin {config.RAINFALL_SENSOR_PIN}")
            except Exception as e:
                logger.error(f"Failed to initialize rainfall sensor: {e}")
        
        # Visual detection parameters
        self.rain_pattern_threshold = 0.7
        self.baseline_frame = None
        self.baseline_count = 0
        
    def detect(self):
        """
        Detect rainfall
        
        Returns:
            bool: True if rainfall detected
        """
        detected = False
        
        # Check hardware sensor
        if self.sensor_available:
            detected = self._check_sensor()
        
        # Visual detection is handled separately in main loop with camera frame
        # This method primarily handles sensor-based detection
        
        return detected
    
    def detect_visual(self, frame):
        """
        Detect rainfall using visual analysis
        
        Args:
            frame (numpy.ndarray): Camera frame
            
        Returns:
            bool: True if rainfall detected visually
        """
        if not self.config.USE_VISUAL_RAINFALL_DETECTION:
            return False
        
        try:
            # Convert to grayscale                                                         
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Build baseline if needed
            if self.baseline_frame is None:
                self._update_baseline(gray)
                return False
            
            # Detect rain streaks using several methods
            
            # Method 1: High-frequency vertical patterns (rain streaks)
            vertical_streaks = self._detect_vertical_streaks(gray)
            
            # Method 2: Temporal variance (rain creates rapid changes)
            temporal_change = self._detect_temporal_changes(gray)
            
            # Method 3: Texture analysis (rain creates specific texture patterns)
            texture_score = self._analyze_rain_texture(gray)
            
            # Combine methods
            rain_confidence = (vertical_streaks + temporal_change + texture_score) / 3.0
            
            is_raining = rain_confidence > self.rain_pattern_threshold
            
            if is_raining:
                self.detection_count += 1
                logger.info(f"Visual rainfall detected (confidence: {rain_confidence:.2f})")
            else:
                self.detection_count = max(0, self.detection_count - 1)
            
            # Update baseline periodically when not raining
            if not is_raining and self.baseline_count % 50 == 0:
                self._update_baseline(gray)
            
            self.baseline_count += 1
            
            # Require multiple consecutive detections to confirm
            return self.detection_count >= 3
            
        except Exception as e:
            logger.error(f"Error in visual rainfall detection: {e}")
            return False
    
    def _check_sensor(self):
        """
        Check hardware rainfall sensor
        
        Returns:
            bool: True if sensor detects rain
        """
        try:
            # Rain sensor typically outputs LOW when rain is detected
            sensor_value = GPIO.input(self.config.RAINFALL_SENSOR_PIN)
            return sensor_value == GPIO.LOW
            
        except Exception as e:
            logger.error(f"Error reading rainfall sensor: {e}")
            return False
    
    def _detect_vertical_streaks(self, gray):
        """Detect vertical rain streaks"""
        # Apply vertical edge detection
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        sobel_y = np.abs(sobel_y)
        
        # Threshold to find strong vertical edges
        _, vertical_edges = cv2.threshold(sobel_y, 50, 255, cv2.THRESH_BINARY)
        
        # Calculate density of vertical edges
        streak_density = np.sum(vertical_edges) / (gray.shape[0] * gray.shape[1] * 255)
        
        return min(1.0, streak_density * 10)
    
    def _detect_temporal_changes(self, gray):
        """Detect rapid temporal changes characteristic of rain"""
        if self.baseline_frame is None:
            return 0.0
        
        # Calculate difference from baseline
        diff = cv2.absdiff(gray, self.baseline_frame)
        
        # Threshold
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        
        # Calculate change ratio
        change_ratio = np.sum(thresh) / (gray.shape[0] * gray.shape[1] * 255)
        
        return min(1.0, change_ratio * 5)
    
    def _analyze_rain_texture(self, gray):
        """Analyze texture patterns typical of rain"""
        # Calculate local binary patterns or texture variance
        # Rain creates high-frequency noise patterns
        
        # Use Laplacian to detect high-frequency content
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()
        
        # Normalize variance score
        texture_score = min(1.0, variance / 1000)
        
        return texture_score
    
    def _update_baseline(self, gray):
        """Update baseline frame for comparison"""
        if self.baseline_frame is None:
            self.baseline_frame = gray.copy()
        else:
            # Exponential moving average
            alpha = 0.1
            self.baseline_frame = cv2.addWeighted(
                gray, alpha,
                self.baseline_frame, 1 - alpha,
                0
            )
    
    def get_intensity(self):
        """
        Get rainfall intensity estimate
        
        Returns:
            str: Intensity level ('light', 'moderate', 'heavy')
        """
        if self.detection_count < 5:
            return 'light'
        elif self.detection_count < 10:
            return 'moderate'
        else:
            return 'heavy'
    
    def cleanup(self):
        """Cleanup GPIO resources"""
        if self.sensor_available and GPIO_AVAILABLE:
            try:
                GPIO.cleanup()
                logger.info("GPIO cleanup completed")
            except Exception as e:
                logger.error(f"Error during GPIO cleanup: {e}")
    
    def __del__(self):
        """Cleanup on deletion"""
        self.cleanup()
