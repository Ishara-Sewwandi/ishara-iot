#!/usr/bin/env python3
"""
Test Your Own Images
Place your fish images in test_images/input/ and run this script
"""

import cv2
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fish_detector import FishDetector
from fish_health_detector import FishHealthDetector
from config import Config


def test_images():
    """Test fish detection and health classification on user images"""
    
    # Setup paths
    input_dir = Path("test_images/input")
    output_dir = Path("test_images/output")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if input directory has images
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
    image_files = [f for f in input_dir.iterdir() 
                   if f.is_file() and f.suffix.lower() in image_extensions]
    
    if not image_files:
        print("=" * 60)
        print("NO IMAGES FOUND!")
        print("=" * 60)
        print(f"\nPlease add images to: {input_dir.absolute()}")
        print("\nSupported formats: JPG, JPEG, PNG, BMP")
        print("\nExample:")
        print(f"  cp your_fish_image.jpg {input_dir}/")
        print("=" * 60)
        return
    
    print("=" * 60)
    print("FISH HEALTH DETECTION - TEST YOUR IMAGES")
    print("=" * 60)
    print(f"\nFound {len(image_files)} image(s) to process\n")
    
    # Initialize config
    config = Config()
    
    # Initialize detectors
    print("Loading models...")
    try:
        fish_detector = FishDetector(config)
        if fish_detector.model is None:
            print("\n⚠️  Fish detection model not found!")
            print("Please train or download the fish detection model first.")
            return
    except Exception as e:
        print(f"\n❌ Error loading fish detector: {e}")
        return
    
    health_detector = FishHealthDetector(config)
    
    if not health_detector.model_available:
        print("\n⚠️  Health classification model not found!")
        print("Using detection only mode.")
    
    print("✓ Models loaded successfully\n")
    
    # Create results file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = output_dir / f"results_{timestamp}.txt"
    
    with open(results_file, 'w') as f:
        f.write("FISH HEALTH DETECTION RESULTS\n")
        f.write("=" * 60 + "\n")
        f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Images Processed: {len(image_files)}\n")
        f.write("=" * 60 + "\n\n")
    
    # Process each image
    for idx, image_path in enumerate(image_files, 1):
        print(f"[{idx}/{len(image_files)}] Processing: {image_path.name}")
        
        # Read image
        img = cv2.imread(str(image_path))
        if img is None:
            print(f"  ✗ Could not read image: {image_path.name}")
            continue
        
        # Detect fish
        detections = fish_detector.detect(img)
        
        # Draw on image
        result_img = img.copy()
        
        if not detections:
            print(f"  ℹ  No fish detected in this image")
            cv2.putText(result_img, "No fish detected", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        else:
            print(f"  ✓ Detected {len(detections)} fish")
            
            # Process each detection
            for i, det in enumerate(detections):
                x1, y1, x2, y2 = det['bbox']
                conf = det['confidence']
                
                # Extract fish region
                fish_crop = img[y1:y2, x1:x2]
                
                # Classify health if model available
                health_status = "Unknown"
                health_conf = 0.0
                color = (255, 0, 0)  # Blue default
                
                if health_detector.model_available and fish_crop.size > 0:
                    health_result = health_detector.classify(fish_crop)
                    if health_result:
                        health_status = health_result['class']
                        health_conf = health_result['confidence']
                        color = health_result['color']
                
                # Draw bounding box
                cv2.rectangle(result_img, (x1, y1), (x2, y2), color, 2)
                
                # Create label
                if health_detector.model_available:
                    label = f"Fish #{i+1}: {health_status} ({health_conf:.1%})"
                else:
                    label = f"Fish #{i+1} (Conf: {conf:.1%})"
                
                # Draw label background
                label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                cv2.rectangle(result_img, (x1, y1 - label_size[1] - 10), 
                            (x1 + label_size[0], y1), color, -1)
                
                # Draw label text
                cv2.putText(result_img, label, (x1, y1 - 5),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                print(f"    Fish #{i+1}: {health_status} (Confidence: {health_conf:.1%})")
        
        # Save result image
        output_path = output_dir / f"result_{image_path.stem}_{timestamp}{image_path.suffix}"
        cv2.imwrite(str(output_path), result_img)
        print(f"  💾 Saved: {output_path.name}\n")
        
        # Write to results file
        with open(results_file, 'a') as f:
            f.write(f"\nImage: {image_path.name}\n")
            f.write("-" * 60 + "\n")
            if not detections:
                f.write("  No fish detected\n")
            else:
                f.write(f"  Total fish detected: {len(detections)}\n\n")
                for i, det in enumerate(detections):
                    x1, y1, x2, y2 = det['bbox']
                    f.write(f"  Fish #{i+1}:\n")
                    f.write(f"    Position: ({x1}, {y1}) to ({x2}, {y2})\n")
                    f.write(f"    Detection Confidence: {det['confidence']:.1%}\n")
                    
                    if health_detector.model_available:
                        fish_crop = img[y1:y2, x1:x2]
                        if fish_crop.size > 0:
                            health_result = health_detector.classify(fish_crop)
                            if health_result:
                                f.write(f"    Health Status: {health_result['class']}\n")
                                f.write(f"    Health Confidence: {health_result['confidence']:.1%}\n")
            f.write("\n")
    
    # Print summary
    print("=" * 60)
    print("PROCESSING COMPLETE!")
    print("=" * 60)
    print(f"\n✓ Processed {len(image_files)} image(s)")
    print(f"✓ Results saved to: {output_dir.absolute()}")
    print(f"✓ Detailed report: {results_file.name}")
    print("\nCheck the output folder for annotated images!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_images()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
