#!/usr/bin/env python3
"""
Camera Handler for Raspberry Pi Camera Module 2
Handles frame capture and image saving using Picamera2
"""

import cv2
import numpy as np
import os
import logging
import threading
import subprocess
import sys

try:
    from picamera2 import Picamera2
    PICAMERA_AVAILABLE = True
except ImportError:
    PICAMERA_AVAILABLE = False
    # Check if system Python has picamera2
    try:
        result = subprocess.run(
            ["/usr/bin/python3", "-c", "from picamera2 import Picamera2; print('OK')"],
            capture_output=True, text=True, timeout=2
        )
        if result.returncode == 0 and "OK" in result.stdout:
            PICAMERA_AVAILABLE = "subprocess"
            logging.info("Picamera2 available via system Python, using subprocess mode")
        else:
            logging.warning("Picamera2 not available, falling back to USB camera")
    except Exception:
        logging.warning("Picamera2 not available, falling back to USB camera")

logger = logging.getLogger(__name__)


class CameraHandler:
    def __init__(self, config):
        """Initialize Raspberry Pi Camera Module 2 or USB camera"""
        self.config = config
        self.camera = None
        self.is_running = False
        self.lock = threading.Lock()
        self.current_frame = None
        self.use_picamera = PICAMERA_AVAILABLE
        
        try:
            if self.use_picamera:
                # Use Raspberry Pi Camera Module 2
                logger.info("Initializing Picamera2...")
                self.camera = Picamera2()
                
                # Configure camera
                camera_config = self.camera.create_video_configuration(
                    main={"size": (config.CAMERA_WIDTH, config.CAMERA_HEIGHT), 
                          "format": "RGB888"},
                    controls={"FrameRate": config.FRAME_RATE},
                    buffer_count=config.CAMERA_BUFFER_COUNT
                )
                
                self.camera.configure(camera_config)
                logger.info(f"Camera configured: {config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT} @ {config.FRAME_RATE}fps")
                print("Picamera2 initialized successfully")
            else:
                # Fallback to Pi Camera via V4L2 or USB camera
                logger.info("Picamera2 not available, trying Pi Camera via V4L2...")
                
                # Try to open Pi Camera on /dev/video0
                self.camera = cv2.VideoCapture(0, cv2.CAP_V4L2)
                
                if not self.camera.isOpened():
                    logger.warning("Could not open /dev/video0, trying other devices...")
                    # Try alternative video devices
                    for device_id in [10, 11, 12]:
                        self.camera = cv2.VideoCapture(device_id, cv2.CAP_V4L2)
                        if self.camera.isOpened():
                            logger.info(f"Successfully opened /dev/video{device_id}")
                            break
                    else:
                        raise Exception("Could not open any camera device")
                
                # Configure camera
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
                self.camera.set(cv2.CAP_PROP_FPS, config.FRAME_RATE)
                self.camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
                
                # Verify camera is working
                ret, test_frame = self.camera.read()
                if not ret or test_frame is None:
                    raise Exception("Camera opened but cannot read frames")
                
                actual_width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
                actual_height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
                logger.info(f"Pi Camera (V4L2) configured: {actual_width}x{actual_height}")
                print(f"Pi Camera initialized successfully via V4L2 ({actual_width}x{actual_height})")
            
        except Exception as e:
            logger.error(f"Failed to initialize camera: {e}")
            raise
    
    def start(self):
        """Start the camera"""
        try:
            if self.use_picamera:
                self.camera.start()
            self.is_running = True
            logger.info("Camera started successfully")
        except Exception as e:
            logger.error(f"Failed to start camera: {e}")
            raise
    
    def stop(self):
        """Stop the camera"""
        if self.camera and self.is_running:
            if self.use_picamera:
                self.camera.stop()
            else:
                self.camera.release()
            self.is_running = False
            logger.info("Camera stopped")
    
    def capture_frame(self):
        """
        Capture a single frame
        
        Returns:
            numpy.ndarray: BGR image frame (OpenCV format)
        """
        try:
            if self.use_picamera:
                # Capture from Picamera2
                frame = self.camera.capture_array("main")
                
                # Convert RGB to BGR (OpenCV format)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            else:
                # Capture from USB camera
                ret, frame = self.camera.read()
                if not ret:
                    return None
            
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
            # Capture fresh frame for streaming
            frame = self.capture_frame()
            
            if frame is None:
                logger.debug("No frame available for streaming")
                return None
            
            # Convert BGR to RGB for web browser display
            # (OpenCV uses BGR, but web browsers expect RGB in JPEG)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame_rgb, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if ret:
                return buffer.tobytes()
            else:
                logger.error("Failed to encode frame as JPEG")
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