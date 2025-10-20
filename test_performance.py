#!/usr/bin/env python3
"""
Performance Test Script
Tests YOLOv8 inference speed with different configurations
"""

import cv2
import time
import numpy as np
from ultralytics import YOLO
from config import Config

def test_yolo_speed():
    """Test YOLOv8 inference speed"""
    config = Config()
    
    print("=" * 60)
    print("Fish Mortality Detection - Performance Test")
    print("=" * 60)
    
    # Create test frame
    test_frame = np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)
    
    # Load model
    print("\nLoading YOLOv8 model...")
    try:
        model = YOLO(config.YOLO_MODEL_PATH)
        print(f"✓ Loaded custom model: {config.YOLO_MODEL_PATH}")
    except:
        model = YOLO('yolov8n.pt')
        print(f"✓ Loaded fallback model: yolov8n.pt")
    
    # Warm up
    print("\nWarming up model (3 iterations)...")
    for _ in range(3):
        _ = model(test_frame, imgsz=config.YOLO_IMG_SIZE, verbose=False)
    
    # Test different image sizes
    image_sizes = [320, 416, 640]
    
    for img_size in image_sizes:
        print(f"\n{'=' * 60}")
        print(f"Testing with image size: {img_size}x{img_size}")
        print(f"{'=' * 60}")
        
        times = []
        for i in range(20):
            start = time.time()
            results = model(
                test_frame,
                imgsz=img_size,
                conf=config.CONFIDENCE_THRESHOLD,
                iou=config.IOU_THRESHOLD,
                verbose=False,
                device='cpu'
            )
            elapsed = time.time() - start
            times.append(elapsed)
            
            if i % 5 == 0:
                print(f"  Iteration {i+1}/20: {elapsed*1000:.1f}ms")
        
        avg_time = np.mean(times)
        fps = 1.0 / avg_time
        
        print(f"\n📊 Results for {img_size}x{img_size}:")
        print(f"  Average inference time: {avg_time*1000:.1f}ms")
        print(f"  Max FPS (detection only): {fps:.1f}")
        print(f"  Min time: {min(times)*1000:.1f}ms")
        print(f"  Max time: {max(times)*1000:.1f}ms")
    
    # Recommendations
    print(f"\n{'=' * 60}")
    print("RECOMMENDATIONS FOR 25 FPS DISPLAY:")
    print(f"{'=' * 60}")
    
    # Calculate optimal SKIP_FRAMES
    for img_size in [320, 416, 640]:
        print(f"\nImage size {img_size}x{img_size}:")
        model_fps = 1.0 / np.mean([t for t in times])  # Rough estimate
        
        for skip in [3, 4, 5, 6, 7]:
            detection_rate = 25 / skip
            load_percent = (1.0 / model_fps) * detection_rate * 100
            
            if load_percent < 80:  # Keep CPU load under 80%
                print(f"  SKIP_FRAMES={skip}: {detection_rate:.1f} det/sec, ~{load_percent:.0f}% CPU load ✓")
            else:
                print(f"  SKIP_FRAMES={skip}: {detection_rate:.1f} det/sec, ~{load_percent:.0f}% CPU load ✗")
    
    print(f"\n{'=' * 60}")
    print("CURRENT CONFIGURATION:")
    print(f"{'=' * 60}")
    print(f"  Camera: {config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT} @ {config.FRAME_RATE}fps")
    print(f"  YOLO image size: {config.YOLO_IMG_SIZE}x{config.YOLO_IMG_SIZE}")
    print(f"  SKIP_FRAMES: {config.SKIP_FRAMES} (detect every {config.SKIP_FRAMES} frames)")
    print(f"  Detection rate: {config.FRAME_RATE / config.SKIP_FRAMES:.1f} detections/second")
    print(f"  Display target: {config.DISPLAY_FPS_TARGET} FPS")
    print()

if __name__ == "__main__":
    test_yolo_speed()
