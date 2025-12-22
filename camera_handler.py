#!/usr/bin/env python3
"""
Camera Handler for Laptop/USB Camera
Handles frame capture and image saving
"""

import cv2
import numpy as np
import os
import logging
import threading

logger = logging.getLogger(__name__)


class CameraHandler:
    def __init__(self, config):
        """Initialize laptop camera"""
        self.config = config
        self.camera = None
        self.is_running = False
        self.lock = threading.Lock()
        self.current_frame = None
        
        try:
            # Use laptop camera (0 is usually the default camera)
            self.camera = cv2.VideoCapture(0)
            
            if not self.camera.isOpened():
                raise Exception("Could not open camera")
            
            # Set camera resolution
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
            self.camera.set(cv2.CAP_PROP_FPS, config.FRAME_RATE)
            
            logger.info(f"Camera configured: {config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT} @ {config.FRAME_RATE}fps")
            print("Camera initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize camera: {e}")
            raise
    
    def start(self):
        """Start the camera"""
        try:
            self.is_running = True
            logger.info("Camera started successfully")
        except Exception as e:
            logger.error(f"Failed to start camera: {e}")
            raise
    
    def stop(self):
        """Stop the camera"""
        if self.camera and self.is_running:
            self.is_running = False
            logger.info("Camera stopped")
    
    def capture_frame(self):
        """
        Capture a single frame
        
        Returns:
            numpy.ndarray: BGR image frame (OpenCV format)
        """
        try:
            ret, frame = self.camera.read()
            if ret:
                # Apply rotation if needed
                if self.config.CAMERA_ROTATION != 0:
                    if self.config.CAMERA_ROTATION == 90:
                        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                    elif self.config.CAMERA_ROTATION == 180:
                        frame = cv2.rotate(frame, cv2.ROTATE_180)
                    elif self.config.CAMERA_ROTATION == 270:
                        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
                
                # Store current frame for streaming
                with self.lock:
                    self.current_frame = frame.copy()
                
                return frame
            return None
            
        except Exception as e:
            logger.error(f"Error capturing frame: {e}")
            return None
    
    def get_frame_for_streaming(self):
        """
        Get the latest frame for streaming (encoded as JPEG)
        
        Returns:
            bytes: JPEG encoded frame
        """
        try:
            with self.lock:
                if self.current_frame is None:
                    # Capture a frame if none exists
                    ret, frame = self.camera.read()
                    if not ret:
                        return None
                else:
                    frame = self.current_frame.copy()
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if ret:
                return buffer.tobytes()
            return None
            
        except Exception as e:
            logger.error(f"Error getting frame for streaming: {e}")
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
    
    def release(self):
        """Release camera resources"""
        if hasattr(self, 'camera') and self.camera:
            self.camera.release()
            cv2.destroyAllWindows()
    
    def __del__(self):
        """Cleanup on deletion"""
        self.stop()
        self.release()

# import cv2
# import numpy as np
# from datetime import datetime
# import os
# import logging
# import threading

# logger = logging.getLogger(__name__)

# class CameraHandler:
#     def __init__(self, config):
#         """Initialize laptop camera"""
#         self.config = config
#         self.camera = None
#         self.is_running = False
#         self.lock = threading.Lock()
#         self.current_frame = None
        
#         try:
#             # Use laptop camera (0 is usually the default camera)
#             self.camera = cv2.VideoCapture(0)
            
#             if not self.camera.isOpened():
#                 raise Exception("Could not open camera")
            
#             # Set camera resolution
#             self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
#             self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
#             self.camera.set(cv2.CAP_PROP_FPS, config.FRAME_RATE)
            
#             logger.info(f"Camera configured: {config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT} @ {config.FRAME_RATE}fps")
#             print("Camera initialized successfully")
            
#         except Exception as e:
#             logger.error(f"Failed to initialize camera: {e}")
#             raise
    
#     def start(self):
#         """Start the camera"""
#         try:
#             self.is_running = True
#             logger.info("Camera started successfully")
#         except Exception as e:
#             logger.error(f"Failed to start camera: {e}")
#             raise
    
#     def stop(self):
#         """Stop the camera"""
#         if self.camera and self.is_running:
#             self.is_running = False
#             logger.info("Camera stopped")
    
#     def capture_frame(self):
#         """
#         Capture a single frame
        
#         Returns:
#             numpy.ndarray: BGR image frame (OpenCV format)
#         """
#         try:
#             ret, frame = self.camera.read()
#             if ret:
#                 # Apply rotation if needed
#                 if self.config.CAMERA_ROTATION != 0:
#                     if self.config.CAMERA_ROTATION == 90:
#                         frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
#                     elif self.config.CAMERA_ROTATION == 180:
#                         frame = cv2.rotate(frame, cv2.ROTATE_180)
#                     elif self.config.CAMERA_ROTATION == 270:
#                         frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
                
#                 # Store current frame for streaming
#                 with self.lock:
#                     self.current_frame = frame.copy()
                
#                 return frame
#             return None
            
#         except Exception as e:
#             logger.error(f"Error capturing frame: {e}")
#             return None
    
#     def get_frame_for_streaming(self):
#         """
#         Get the latest frame for streaming (encoded as JPEG)
        
#         Returns:
#             bytes: JPEG encoded frame
#         """
#         try:
#             with self.lock:
#                 if self.current_frame is None:
#                     # Capture a frame if none exists
#                     ret, frame = self.camera.read()
#                     if not ret:
#                         return None
#                 else:
#                     frame = self.current_frame.copy()
            
#             # Encode frame as JPEG
#             ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
#             if ret:
#                 return buffer.tobytes()
#             return None
            
#         except Exception as e:
#             logger.error(f"Error getting frame for streaming: {e}")
#             return None
    
#     def save_image(self, frame, filename):
#         """
#         Save frame to disk
        
#         Args:
#             frame (numpy.ndarray): Image frame
#             filename (str): Filename for saved image
            
#         Returns:
#             str: Full path to saved image
#         """
#         try:
#             filepath = os.path.join(self.config.IMAGE_SAVE_DIR, filename)
#             cv2.imwrite(filepath, frame)
#             logger.info(f"Image saved: {filepath}")
            
#             # Cleanup old images if necessary
#             self._cleanup_old_images()
            
#             return filepath
            
#         except Exception as e:
#             logger.error(f"Error saving image: {e}")
#             return None
    
#     def _cleanup_old_images(self):
#         """Remove old images if exceeding max storage"""
#         try:
#             images = sorted([
#                 os.path.join(self.config.IMAGE_SAVE_DIR, f)
#                 for f in os.listdir(self.config.IMAGE_SAVE_DIR)
#                 if f.endswith(('.jpg', '.png'))
#             ], key=os.path.getctime)
            
#             while len(images) > self.config.MAX_STORED_IMAGES:
#                 oldest = images.pop(0)
#                 os.remove(oldest)
#                 logger.info(f"Removed old image: {oldest}")
                
#         except Exception as e:
#             logger.error(f"Error cleaning up old images: {e}")
    
#     def release(self):
#         """Release camera resources"""
#         if hasattr(self, 'camera') and self.camera:
#             self.camera.release()
#             cv2.destroyAllWindows()
    
#     def __del__(self):
#         """Cleanup on deletion"""
#         self.stop()
#         self.release()