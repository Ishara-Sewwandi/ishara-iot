#!/usr/bin/env python3
"""
Advanced Fish Behavior Dataset Collection Tool
Captures and labels fish with specific behaviors:
- Healthy fish (fins moving)
- Sick fish (fins not moving)
- Side-floating fish
- Dead fish
"""

import cv2
import os
import json
import time
import argparse
from datetime import datetime
from camera_handler import CameraHandler
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BehaviorDatasetCollector:
    """Interactive dataset collection tool for fish behavior"""
    
    BEHAVIORS = {
        '1': {'name': 'healthy', 'label': 'Healthy fish with moving fins', 'color': (0, 255, 0)},
        '2': {'name': 'fins_not_moving', 'label': 'Fish with inactive fins', 'color': (0, 165, 255)},
        '3': {'name': 'side_floating', 'label': 'Fish floating on side', 'color': (0, 0, 255)},
        '4': {'name': 'dead', 'label': 'Dead fish', 'color': (128, 0, 128)},
        '5': {'name': 'normal_floating', 'label': 'Normal surface floating', 'color': (255, 255, 0)},
        '6': {'name': 'lethargic', 'label': 'Lethargic/slow movement', 'color': (255, 165, 0)}
    }
    
    def __init__(self, output_dir, config):
        self.output_dir = output_dir
        self.config = config
        self.camera = None
        self.current_behavior = None
        self.capture_count = 0
        self.session_data = []
        
        # Create directories
        self.images_dir = os.path.join(output_dir, 'images')
        self.labels_dir = os.path.join(output_dir, 'labels')
        self.metadata_dir = os.path.join(output_dir, 'metadata')
        
        for d in [self.images_dir, self.labels_dir, self.metadata_dir]:
            os.makedirs(d, exist_ok=True)
    
    def start(self):
        """Start the dataset collection interface"""
        self.camera = CameraHandler(self.config)
        self.camera.start()
        
        cv2.namedWindow('Fish Behavior Dataset Collector', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Fish Behavior Dataset Collector', 1280, 720)
        
        logger.info("=" * 70)
        logger.info("Fish Behavior Dataset Collector Started")
        logger.info("=" * 70)
        logger.info("Instructions:")
        logger.info("  1. Select behavior type (1-6)")
        logger.info("  2. Click to draw bounding box around fish")
        logger.info("  3. Press SPACE to save labeled image")
        logger.info("  4. Press ESC to cancel current box")
        logger.info("  5. Press Q to quit")
        logger.info("=" * 70)
        
        self.show_behavior_menu()
        
        try:
            self.main_loop()
        finally:
            self.cleanup()
    
    def show_behavior_menu(self):
        """Display behavior selection menu"""
        print("\n" + "=" * 70)
        print("SELECT FISH BEHAVIOR:")
        print("=" * 70)
        for key, behavior in self.BEHAVIORS.items():
            print(f"  {key}. {behavior['label']}")
        print("=" * 70)
        
        choice = input("Select behavior (1-6): ").strip()
        
        if choice in self.BEHAVIORS:
            self.current_behavior = choice
            behavior = self.BEHAVIORS[choice]
            logger.info(f"✓ Selected: {behavior['label']}")
            print(f"\n📸 Now capture images of: {behavior['label']}")
            print("   Click and drag to draw box around fish, then press SPACE\n")
        else:
            logger.warning("Invalid choice, defaulting to 'healthy'")
            self.current_behavior = '1'
    
    def main_loop(self):
        """Main collection loop with interactive labeling"""
        drawing = False
        start_point = None
        current_box = None
        boxes = []
        
        def mouse_callback(event, x, y, flags, param):
            nonlocal drawing, start_point, current_box, boxes
            
            if event == cv2.EVENT_LBUTTONDOWN:
                drawing = True
                start_point = (x, y)
                current_box = None
            
            elif event == cv2.EVENT_MOUSEMOVE and drawing:
                current_box = (start_point[0], start_point[1], x, y)
            
            elif event == cv2.EVENT_LBUTTONUP:
                drawing = False
                if start_point:
                    x1, y1 = start_point
                    x2, y2 = x, y
                    
                    # Ensure valid box
                    if abs(x2 - x1) > 10 and abs(y2 - y1) > 10:
                        box = {
                            'coords': (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)),
                            'behavior': self.current_behavior
                        }
                        boxes.append(box)
                        logger.info(f"✓ Box added: {self.BEHAVIORS[self.current_behavior]['label']}")
                
                start_point = None
                current_box = None
        
        cv2.setMouseCallback('Fish Behavior Dataset Collector', mouse_callback)
        
        while True:
            frame = self.camera.capture_frame()
            if frame is None:
                time.sleep(0.01)
                continue
            
            display = frame.copy()
            h, w = display.shape[:2]
            
            # Draw existing boxes
            for box in boxes:
                x1, y1, x2, y2 = box['coords']
                behavior = self.BEHAVIORS[box['behavior']]
                color = behavior['color']
                
                cv2.rectangle(display, (x1, y1), (x2, y2), color, 2)
                
                # Label
                label = behavior['name']
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                cv2.rectangle(display, (x1, y1 - label_size[1] - 10), 
                            (x1 + label_size[0] + 10, y1), color, -1)
                cv2.putText(display, label, (x1 + 5, y1 - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            # Draw current box being drawn
            if current_box:
                x1, y1, x2, y2 = current_box
                behavior = self.BEHAVIORS[self.current_behavior]
                cv2.rectangle(display, (x1, y1), (x2, y2), behavior['color'], 2)
            
            # Draw info panel
            panel_height = 200
            overlay = display.copy()
            cv2.rectangle(overlay, (0, 0), (w, panel_height), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.7, display, 0.3, 0, display)
            
            # Title
            cv2.putText(display, "Fish Behavior Dataset Collector", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            
            # Current behavior
            behavior = self.BEHAVIORS[self.current_behavior]
            cv2.putText(display, f"Current: {behavior['label']}", (10, 65),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, behavior['color'], 2)
            
            # Stats
            cv2.putText(display, f"Boxes: {len(boxes)} | Captured: {self.capture_count}", 
                       (10, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Instructions
            cv2.putText(display, "Click & drag to draw box | SPACE: Save | ESC: Clear | C: Change behavior | Q: Quit",
                       (10, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            
            # Behavior legend
            y_offset = 155
            for key, beh in self.BEHAVIORS.items():
                prefix = "→ " if key == self.current_behavior else "  "
                cv2.putText(display, f"{prefix}{key}: {beh['name']}", (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, beh['color'], 1)
                y_offset += 20
            
            cv2.imshow('Fish Behavior Dataset Collector', display)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord(' ') and boxes:
                # Save image with labels
                self.save_labeled_image(frame, boxes)
                boxes = []
            
            elif key == 27:  # ESC - clear boxes
                boxes = []
                logger.info("Boxes cleared")
            
            elif key == ord('c'):
                # Change behavior
                self.show_behavior_menu()
                boxes = []
            
            elif key in [ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6')]:
                # Quick behavior change
                self.current_behavior = chr(key)
                behavior = self.BEHAVIORS[self.current_behavior]
                logger.info(f"✓ Switched to: {behavior['label']}")
            
            elif key == ord('q'):
                break
    
    def save_labeled_image(self, frame, boxes):
        """Save image and YOLO format labels"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_filename = f'fish_{self.capture_count:04d}_{timestamp}.jpg'
        label_filename = f'fish_{self.capture_count:04d}_{timestamp}.txt'
        
        image_path = os.path.join(self.images_dir, image_filename)
        label_path = os.path.join(self.labels_dir, label_filename)
        
        # Save image
        cv2.imwrite(image_path, frame)
        
        # Save YOLO format labels
        h, w = frame.shape[:2]
        with open(label_path, 'w') as f:
            for box in boxes:
                x1, y1, x2, y2 = box['coords']
                behavior_id = int(box['behavior']) - 1  # 0-indexed for YOLO
                
                # Convert to YOLO format (normalized center x, y, width, height)
                center_x = ((x1 + x2) / 2) / w
                center_y = ((y1 + y2) / 2) / h
                box_w = abs(x2 - x1) / w
                box_h = abs(y2 - y1) / h
                
                f.write(f"{behavior_id} {center_x:.6f} {center_y:.6f} {box_w:.6f} {box_h:.6f}\n")
        
        # Save metadata (human-readable)
        metadata = {
            'filename': image_filename,
            'timestamp': timestamp,
            'boxes': [
                {
                    'behavior': self.BEHAVIORS[box['behavior']]['name'],
                    'label': self.BEHAVIORS[box['behavior']]['label'],
                    'coords': box['coords']
                }
                for box in boxes
            ]
        }
        
        metadata_path = os.path.join(self.metadata_dir, 
                                     f'fish_{self.capture_count:04d}_{timestamp}.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.session_data.append(metadata)
        self.capture_count += 1
        
        logger.info(f"✓ Saved: {image_filename} with {len(boxes)} boxes")
    
    def cleanup(self):
        """Cleanup and save session summary"""
        if self.camera:
            self.camera.stop()
        
        cv2.destroyAllWindows()
        
        # Save session summary
        summary = {
            'total_images': self.capture_count,
            'date': datetime.now().isoformat(),
            'behavior_counts': {},
            'images': self.session_data
        }
        
        # Count behaviors
        for behavior_key in self.BEHAVIORS:
            count = sum(
                1 for img in self.session_data 
                for box in img['boxes'] 
                if box['behavior'] == self.BEHAVIORS[behavior_key]['name']
            )
            if count > 0:
                summary['behavior_counts'][self.BEHAVIORS[behavior_key]['name']] = count
        
        summary_path = os.path.join(self.output_dir, 'session_summary.json')
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info("\n" + "=" * 70)
        logger.info("Collection Session Complete")
        logger.info("=" * 70)
        logger.info(f"Total images: {self.capture_count}")
        logger.info(f"Saved to: {self.output_dir}")
        logger.info("\nBehavior counts:")
        for behavior, count in summary['behavior_counts'].items():
            logger.info(f"  {behavior}: {count}")
        logger.info("=" * 70)
        
        print("\n✓ Dataset collection complete!")
        print(f"\nNext steps:")
        print(f"1. Review images in: {self.images_dir}")
        print(f"2. Check labels in: {self.labels_dir}")
        print(f"3. Split into train/val sets")
        print(f"4. Train model: python3 train_model.py")


def main():
    parser = argparse.ArgumentParser(
        description='Fish Behavior Dataset Collection Tool - Interactive Labeling'
    )
    parser.add_argument('--output', type=str, default='dataset/behavior_data',
                       help='Output directory (default: dataset/behavior_data)')
    
    args = parser.parse_args()
    
    config = Config()
    
    print("\n" + "=" * 70)
    print("Fish Behavior Dataset Collector")
    print("Advanced Interactive Labeling Tool")
    print("=" * 70)
    print("\nThis tool helps you create a dataset for detecting:")
    print("  • Healthy fish (fins moving)")
    print("  • Sick fish (fins not moving)")
    print("  • Side-floating fish")
    print("  • Dead fish")
    print("  • Other behavior patterns")
    print("\nYou will:")
    print("  1. Select a behavior category")
    print("  2. Draw boxes around fish showing that behavior")
    print("  3. Label multiple fish per image")
    print("  4. Build a comprehensive training dataset")
    print("=" * 70)
    
    input("\nPress ENTER to start...")
    
    collector = BehaviorDatasetCollector(args.output, config)
    collector.start()


if __name__ == "__main__":
    main()
