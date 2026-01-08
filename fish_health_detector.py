#!/usr/bin/env python3
"""
Fish Health Detection Module
Classifies fish health status from images
"""

import cv2
import numpy as np
from ultralytics import YOLO
import logging
import os

logger = logging.getLogger(__name__)


class FishHealthDetector:
    """Fish health classification using YOLOv8"""
    
    def __init__(self, config=None, confidence_threshold=0.65):
        """Initialize fish health classifier
        
        Args:
            config: Configuration object
            confidence_threshold: Minimum confidence for predictions (default: 0.65)
                                 Set higher (0.75-0.85) for more reliable detection
                                 Set lower (0.50-0.60) for more sensitive detection
        """
        self.config = config
        self.model = None
        self.model_available = False
        self.confidence_threshold = confidence_threshold
        
        # Health class names (alphabetically as YOLOv8 will sort them)
        # Simplified 3-class system: dead, healthy, unhealthy
        self.class_names = [
            'dead',
            'healthy',
            'unhealthy'
        ]
        
        # Severity levels
        self.severity = {
            'healthy': 0,
            'unhealthy': 2,
            'dead': 3
        }
        
        # Color codes for display
        self.colors = {
            'healthy': (0, 255, 0),      # Green
            'unhealthy': (0, 165, 255),  # Orange
            'dead': (0, 0, 255)          # Red
        }
        
        try:
            model_path = 'models/fish_health_classifier.pt'
            if os.path.exists(model_path):
                self.model = YOLO(model_path)
                self.model_available = True
                logger.info(f"Fish health classifier loaded: {model_path}")
                print("✅ Fish health classifier loaded successfully")
            else:
                logger.warning(f"Health classifier not found: {model_path}")
                print(f"⚠️ Fish health classifier not found: {model_path}")
                print("Train the model first: python3 train_fish_health_classifier.py")
        except Exception as e:
            logger.error(f"Failed to load health classifier: {e}")
            print(f"❌ Failed to load health classifier: {e}")
    
    def classify(self, fish_image):
        """
        Classify fish health status
        
        Args:
            fish_image: Cropped image of a single fish (numpy array)
            
        Returns:
            dict with 'class', 'confidence', 'severity', etc. or None
        """
        if not self.model_available or self.model is None:
            return None
        
        try:
            # Ensure image is valid
            if fish_image is None or fish_image.size == 0:
                return None
            
            # Run classification
            results = self.model(fish_image, verbose=False)
            
            if len(results) > 0:
                result = results[0]
                probs = result.probs
                
                # Get top prediction
                top_class_id = int(probs.top1)
                confidence = float(probs.top1conf)
                
                # Get class name
                if top_class_id < len(self.class_names):
                    class_name = self.class_names[top_class_id]
                else:
                    class_name = f"class_{top_class_id}"
                
                # Apply confidence threshold
                if confidence < self.confidence_threshold:
                    # Low confidence - return uncertain status
                    return {
                        'class': 'uncertain',
                        'confidence': confidence,
                        'severity': 1,
                        'is_healthy': False,
                        'needs_attention': False,
                        'is_critical': False,
                        'uncertain': True,
                        'probable_class': class_name,  # Show what it might be
                        'color': (128, 128, 128)  # Gray for uncertain
                    }
                
                # High confidence prediction
                return {
                    'class': class_name,
                    'confidence': confidence,
                    'severity': self.severity.get(class_name, 1),
                    'is_healthy': class_name == 'healthy',
                    'needs_attention': class_name != 'healthy',
                    'is_critical': class_name == 'dead',
                    'uncertain': False,
                    'color': self.colors.get(class_name, (255, 255, 255))
                }
            
        except Exception as e:
            logger.error(f"Error in health classification: {e}")
        
        return None
    
    def get_color_for_health(self, health_class):
        """Get color code for health status (BGR format)"""
        return self.colors.get(health_class, (255, 255, 255))
    
    def get_severity_level(self, health_class):
        """Get severity level (0=healthy, 3=critical)"""
        return self.severity.get(health_class, 1)


def test_classifier():
    """Test the fish health classifier on sample images"""
    import sys
    
    print("\n" + "=" * 60)
    print("Fish Health Classifier Test")
    print("=" * 60)
    
    # Initialize detector
    detector = FishHealthDetector()
    
    if not detector.model_available:
        print("\n❌ Model not available. Train it first:")
        print("   python3 train_fish_health_classifier.py")
        return
    
    # Test on validation images
    dataset_path = 'dataset/fish_health/val'
    
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset not found: {dataset_path}")
        return
    
    print(f"\n� Testing on validation images...")
    
    # Test each class
    for class_name in detector.class_names:
        class_dir = os.path.join(dataset_path, class_name)
        if not os.path.exists(class_dir):
            continue
        
        images = [f for f in os.listdir(class_dir) if f.endswith(('.jpg', '.png'))]
        
        if len(images) == 0:
            continue
        
        print(f"\n📊 Testing class: {class_name} ({len(images)} images)")
        
        correct = 0
        total = 0
        
        # Test first 10 images
        for img_file in images[:10]:
            img_path = os.path.join(class_dir, img_file)
            img = cv2.imread(img_path)
            
            if img is None:
                continue
            
            result = detector.classify(img)
            
            if result:
                total += 1
                if result['class'] == class_name:
                    correct += 1
                
                print(f"  {img_file[:30]:30s} → {result['class']:12s} ({result['confidence']:.2%})")
        
        if total > 0:
            accuracy = correct / total * 100
            print(f"  Accuracy: {correct}/{total} = {accuracy:.1f}%")
    
    print("\n✅ Test complete!")
    print("\nNext: Run full monitoring system")
    print("   python3 main_with_health.py")


if __name__ == "__main__":
    test_classifier()
