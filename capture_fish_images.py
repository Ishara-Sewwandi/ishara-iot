#!/usr/bin/env python3
"""
Fish Image Capture Tool
Collect images from your pond for training YOLOv8
"""

import cv2
import os
import time
import argparse
from camera_handler import CameraHandler
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def manual_capture(output_dir, config):
    """Manual image capture - press SPACE to save"""
    logger.info("Manual capture mode")
    logger.info("Press SPACE to capture, Q to quit")
    
    camera = CameraHandler(config)
    camera.start()
    
    count = 0
    cv2.namedWindow('Fish Image Capture', cv2.WINDOW_NORMAL)
    
    try:
        while True:
            frame = camera.capture_frame()
            if frame is None:
                time.sleep(0.01)
                continue
            
            # Show frame with instructions
            display = frame.copy()
            cv2.putText(display, "Press SPACE to capture, Q to quit", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(display, f"Captured: {count} images", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            cv2.imshow('Fish Image Capture', display)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' '):
                filename = os.path.join(output_dir, f'fish_{count:04d}.jpg')
                cv2.imwrite(filename, frame)
                logger.info(f"✓ Saved: {filename}")
                count += 1
            elif key == ord('q'):
                logger.info(f"Quit. Total images captured: {count}")
                break
    
    finally:
        camera.stop()
        cv2.destroyAllWindows()


def auto_capture(output_dir, config, num_images, interval):
    """Automatic image capture at intervals"""
    logger.info(f"Auto capture mode: {num_images} images, {interval}s interval")
    
    camera = CameraHandler(config)
    camera.start()
    
    cv2.namedWindow('Fish Image Capture', cv2.WINDOW_NORMAL)
    
    try:
        for i in range(num_images):
            frame = camera.capture_frame()
            if frame is None:
                logger.warning(f"Failed to capture frame {i}")
                continue
            
            filename = os.path.join(output_dir, f'capture_{i:04d}.jpg')
            cv2.imwrite(filename, frame)
            logger.info(f"✓ [{i+1}/{num_images}] Saved: {filename}")
            
            # Show preview
            display = frame.copy()
            cv2.putText(display, f"Auto-capturing: {i+1}/{num_images}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(display, f"Next in {interval}s", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.imshow('Fish Image Capture', display)
            cv2.waitKey(1)
            
            if i < num_images - 1:
                time.sleep(interval)
    
    finally:
        camera.stop()
        cv2.destroyAllWindows()
        logger.info(f"✓ Complete! Captured {num_images} images")


def time_lapse_capture(output_dir, config, duration_minutes, interval):
    """Time-lapse capture over a period"""
    logger.info(f"Time-lapse mode: {duration_minutes} minutes, {interval}s interval")
    
    num_images = int((duration_minutes * 60) / interval)
    logger.info(f"Will capture ~{num_images} images")
    
    camera = CameraHandler(config)
    camera.start()
    
    cv2.namedWindow('Fish Time-Lapse Capture', cv2.WINDOW_NORMAL)
    
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    count = 0
    
    try:
        while time.time() < end_time:
            frame = camera.capture_frame()
            if frame is not None:
                filename = os.path.join(output_dir, f'timelapse_{count:04d}.jpg')
                cv2.imwrite(filename, frame)
                
                remaining = int(end_time - time.time())
                logger.info(f"✓ [{count+1}] {filename} (remaining: {remaining}s)")
                
                # Show preview
                display = frame.copy()
                cv2.putText(display, f"Time-lapse: {count+1} images", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(display, f"Time remaining: {remaining//60}m {remaining%60}s", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                cv2.imshow('Fish Time-Lapse Capture', display)
                cv2.waitKey(1)
                
                count += 1
            
            time.sleep(interval)
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    
    finally:
        camera.stop()
        cv2.destroyAllWindows()
        logger.info(f"✓ Complete! Captured {count} images over {duration_minutes} minutes")


def main():
    parser = argparse.ArgumentParser(description='Fish Image Capture Tool for YOLOv8 Training')
    parser.add_argument('--mode', type=str, default='manual',
                       choices=['manual', 'auto', 'timelapse'],
                       help='Capture mode (default: manual)')
    parser.add_argument('--output', type=str, default='dataset/images/raw',
                       help='Output directory (default: dataset/images/raw)')
    parser.add_argument('--num', type=int, default=100,
                       help='Number of images (auto mode, default: 100)')
    parser.add_argument('--interval', type=int, default=1,
                       help='Interval in seconds (default: 1)')
    parser.add_argument('--duration', type=int, default=60,
                       help='Duration in minutes (timelapse mode, default: 60)')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    config = Config()
    
    print("=" * 60)
    print("Fish Image Capture Tool")
    print("=" * 60)
    print(f"Mode: {args.mode}")
    print(f"Output: {args.output}")
    print(f"Camera: {config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT}")
    print("=" * 60)
    print()
    
    if args.mode == 'manual':
        manual_capture(args.output, config)
    elif args.mode == 'auto':
        auto_capture(args.output, config, args.num, args.interval)
    elif args.mode == 'timelapse':
        time_lapse_capture(args.output, config, args.duration, args.interval)
    
    print()
    print("=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print(f"1. Review images in: {args.output}")
    print("2. Delete bad images (blurry, empty, etc.)")
    print("3. Annotate images using:")
    print("   - LabelImg: pip install labelImg && labelImg")
    print("   - Roboflow: https://roboflow.com (recommended)")
    print("   - CVAT: https://app.cvat.ai")
    print("4. Organize into train/val/test folders")
    print("5. Train model: python3 train_model.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
