#!/usr/bin/env python3
"""
Camera Handler for Pi Camera Module 2
Handles frame capture and image saving
"""

import cv2
import numpy as np
from picamera2 import Picamera2
import os
import logging

logger = logging.getLogger(__name__)


class CameraHandler:
    def __init__(self, config):
        """Initialize Pi Camera Module 2"""
        self.config = config
        self.camera = None
        self.is_running = False
        
        try:
            # Initialize Picamera2 (for Pi Camera Module 2)
            self.camera = Picamera2()
            
            # Configure camera with the correct API
            config_dict = self.camera.create_video_configuration(
                main={"size": (config.CAMERA_WIDTH, config.CAMERA_HEIGHT), "format": "RGB888"}
            )
            
            self.camera.configure(config_dict)
            logger.info(f"Camera configured: {config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT} @ {config.FRAME_RATE}fps")
            
        except Exception as e:
            logger.error(f"Failed to initialize camera: {e}")
            raise
    
    def start(self):
        """Start the camera"""
        try:
            self.camera.start()
            self.is_running = True
            logger.info("Camera started successfully")
        except Exception as e:
            logger.error(f"Failed to start camera: {e}")
            raise
    
    def stop(self):
        """Stop the camera"""
        if self.camera and self.is_running:
            self.camera.stop()
            self.is_running = False
            logger.info("Camera stopped")
    
    def capture_frame(self):
        """
        Capture a single frame (Optimized for speed)
        
        Returns:
            numpy.ndarray: BGR image frame (OpenCV format)
        """
        try:
            if not self.is_running:
                logger.warning("Camera not running")
                return None
            
            # Capture frame as numpy array (RGB) - fastest method
            frame = self.camera.capture_array("main")
            
            # Convert RGB to BGR for OpenCV (in-place for speed)
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Apply rotation if needed (optimized)
            if self.config.CAMERA_ROTATION != 0:
                if self.config.CAMERA_ROTATION == 90:
                    frame_bgr = cv2.rotate(frame_bgr, cv2.ROTATE_90_CLOCKWISE)
                elif self.config.CAMERA_ROTATION == 180:
                    frame_bgr = cv2.rotate(frame_bgr, cv2.ROTATE_180)
                elif self.config.CAMERA_ROTATION == 270:
                    frame_bgr = cv2.rotate(frame_bgr, cv2.ROTATE_90_COUNTERCLOCKWISE)
            
            return frame_bgr
            
        except Exception as e:
            logger.error(f"Error capturing frame: {e}")
            return None
    
    def save_image(self, frame, filename):
        """
        Save frame to disk
        
        Args:
            frame (numpy.ndarray): Image frame
            filename (str): Filename for saved image
            
        Returns:
            str: Full path to saved image
        """
        try:
            filepath = os.path.join(self.config.IMAGE_SAVE_DIR, filename)
            cv2.imwrite(filepath, frame)
            logger.info(f"Image saved: {filepath}")
            
            # Cleanup old images if necessary
            self._cleanup_old_images()
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving image: {e}")
            return None
    
    def _cleanup_old_images(self):
        """Remove old images if exceeding max storage"""
        try:
            images = sorted([
                os.path.join(self.config.IMAGE_SAVE_DIR, f)
                for f in os.listdir(self.config.IMAGE_SAVE_DIR)
                if f.endswith(('.jpg', '.png'))
            ], key=os.path.getctime)
            
            while len(images) > self.config.MAX_STORED_IMAGES:
                oldest = images.pop(0)
                os.remove(oldest)
                logger.info(f"Removed old image: {oldest}")
                
        except Exception as e:
            logger.error(f"Error cleaning up old images: {e}")
    
    def __del__(self):
        """Cleanup on deletion"""
        self.stop()
