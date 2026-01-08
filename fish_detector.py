#!/usr/bin/env python3
"""
Fish Detection using YOLOv8
Detects fish in video frames
"""

import cv2
import numpy as np
from ultralytics import YOLO
import logging

logger = logging.getLogger(__name__)


class FishDetector:
    def __init__(self, config):
        """Initialize YOLOv8 fish detector"""
        self.config = config
        self.model = None
        
        try:
            # Load YOLOv8 model
            self.model = YOLO(config.YOLO_MODEL_PATH)
            logger.info(f"YOLOv8 model loaded: {config.YOLO_MODEL_PATH}")
            
        except Exception as e:
            logger.error(f"Failed to load YOLOv8 model: {e}")
            logger.info("You can download a pre-trained model or train your own")
            logger.info("For now, using YOLOv8n as fallback")
            try:
                self.model = YOLO('yolov8n.pt')  # Fallback to nano model
            except:
                raise Exception("Could not load any YOLO model")
    
    def _enhance_frame(self, frame):
        """
        Enhance frame for better fish detection (lightweight version)
        - Improve contrast
        - Slight brightness adjustment
        
        Args:
            frame (numpy.ndarray): Input frame
            
        Returns:
            numpy.ndarray: Enhanced frame
        """
        try:
            # Convert to LAB color space for better contrast processing
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to L channel
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            # Merge channels back
            enhanced_lab = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
            
            return enhanced
            
        except Exception as e:
            logger.warning(f"Frame enhancement failed, using original: {e}")
            return frame
    
    def detect(self, frame):
        """
        Detect fish in frame using YOLOv8
        
        Args:
            frame (numpy.ndarray): Input frame
            
        Returns:
            list: List of detections with format:
                  [{'bbox': [x1, y1, x2, y2], 'confidence': float, 'class': str}]
        """
        try:
            # Enhance frame for better detection
            enhanced_frame = self._enhance_frame(frame)
            
            # Run inference with optimized settings for Raspberry Pi
            results = self.model(
                enhanced_frame,
                conf=self.config.CONFIDENCE_THRESHOLD,
                iou=self.config.IOU_THRESHOLD,
                imgsz=self.config.YOLO_IMG_SIZE,  # Image size for detection
                half=self.config.YOLO_HALF,  # Half precision if GPU available
                max_det=self.config.YOLO_MAX_DET,  # Maximum detections
                agnostic_nms=self.config.YOLO_AGNOSTIC_NMS,  # Faster NMS
                verbose=False,
                device='cpu'  # Force CPU on Raspberry Pi
            )
            
            detections = []
            
            # Parse results
            for result in results:
                boxes = result.boxes
                
                for box in boxes:
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = float(box.conf[0].cpu().numpy())
                    class_id = int(box.cls[0].cpu().numpy())
                    class_name = self.model.names[class_id]
                    
                    detection = {
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'confidence': confidence,
                        'class': class_name,
                        'class_id': class_id
                    }
                    
                    detections.append(detection)
            
            if self.config.VERBOSE and detections:
                logger.debug(f"Detected {len(detections)} fish")
            
            return detections
            
        except Exception as e:
            logger.error(f"Error in fish detection: {e}")
            return []
    
    def draw_detections(self, frame, detections):
        """
        Draw bounding boxes on frame
        
        Args:
            frame (numpy.ndarray): Input frame
            detections (list): List of detections
            
        Returns:
            numpy.ndarray: Frame with drawn detections
        """
        frame_copy = frame.copy()
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            confidence = det['confidence']
            class_name = det['class']
            
            # Draw bounding box
            cv2.rectangle(frame_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(
                frame_copy,
                (x1, y1 - label_size[1] - 10),
                (x1 + label_size[0], y1),
                (0, 255, 0),
                -1
            )
            cv2.putText(
                frame_copy,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                2
            )
        
        return frame_copy


if __name__ == "__main__":
    # Test the detector
    print("Testing Fish Detector...")
    from config import Config
    
    config = Config()
    detector = FishDetector(config)
    
    # Test with a sample image
    test_img = cv2.imread("test_images/input/test.jpg")
    if test_img is not None:
        detections = detector.detect(test_img)
        print(f"Detected {len(detections)} fish")
        
        result = detector.draw_detections(test_img, detections)
        cv2.imwrite("test_detection_output.jpg", result)
        print("Result saved to test_detection_output.jpg")
    else:
        print("No test image found at test_images/input/test.jpg")
