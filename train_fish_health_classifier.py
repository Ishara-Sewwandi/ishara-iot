#!/usr/bin/env python3
"""
Fish Health Classification Model Training
Trains YOLOv8 classification model on fish health dataset
"""

import argparse
import os
from pathlib import Path
from ultralytics import YOLO
import time

def train_fish_health_model(args):
    """Train YOLOv8 classification model"""
    
    print("\n" + "=" * 60)
    print("Fish Health Classification Training")
    print("=" * 60)
    print(f"Dataset: {args.data}")
    print(f"Epochs: {args.epochs}")
    print(f"Image size: {args.imgsz}")
    print(f"Batch size: {args.batch}")
    print(f"Device: {args.device}")
    print("=" * 60)
    
    # Validate dataset structure
    data_path = Path(args.data)
    if not data_path.exists():
        print(f"❌ Dataset not found: {args.data}")
        return
    
    train_dir = data_path / 'train'
    val_dir = data_path / 'val'
    test_dir = data_path / 'test'
    
    if not all([train_dir.exists(), val_dir.exists()]):
        print("❌ Missing train or val directories")
        return
    
    # Count images per class
    print("\n📊 Dataset Statistics:")
    total_all = 0
    for split in ['train', 'val', 'test']:
        split_dir = data_path / split
        if split_dir.exists():
            classes = sorted([d.name for d in split_dir.iterdir() if d.is_dir()])
            print(f"\n{split.upper()}:")
            total = 0
            for cls in classes:
                count = len(list((split_dir / cls).glob('*.jpg'))) + \
                       len(list((split_dir / cls).glob('*.png')))
                print(f"  {cls}: {count} images")
                total += count
            print(f"  Total: {total} images")
            total_all += total
    
    print(f"\n📦 Total dataset: {total_all} images")
    print(f"\n3 Classes: dead, healthy, unhealthy")
    
    # Load YOLOv8 classification model
    print(f"\n📦 Loading model: {args.model}")
    model = YOLO(args.model)
    
    # Train
    print("\n🚀 Starting training...")
    print("This will take 1-3 hours on Raspberry Pi 4")
    print("Press Ctrl+C to stop training\n")
    
    start_time = time.time()
    
    try:
        results = model.train(
            data=str(data_path),
            epochs=args.epochs,
            imgsz=args.imgsz,
            batch=args.batch,
            device=args.device,
            workers=2,
            patience=0,  # Disable early stopping to train full epochs
            save=True,
            plots=True,
            verbose=True,
            name='fish_health',
            project='runs/classify',
            # Enhanced augmentation for small balanced dataset
            hsv_h=0.015,       # Hue augmentation
            hsv_s=0.7,         # Saturation augmentation  
            hsv_v=0.4,         # Value augmentation
            degrees=15,        # Rotation
            translate=0.1,     # Translation
            scale=0.5,         # Scaling
            flipud=0.5,        # Vertical flip
            fliplr=0.5,        # Horizontal flip
            mosaic=0.0,        # Disable mosaic (not good for classification)
            mixup=0.0          # Disable mixup
        )
        
        elapsed = time.time() - start_time
        print(f"\n✅ Training completed in {elapsed/3600:.2f} hours!")
        
        # Get the actual save directory from results
        save_dir = Path(results.save_dir) if hasattr(results, 'save_dir') else Path('runs/classify/fish_health')
        best_model_path = save_dir / 'weights' / 'best.pt'
        
        print(f"Best model location: {best_model_path}")
        
        # Copy best model to models directory
        os.makedirs('models', exist_ok=True)
        import shutil
        
        if best_model_path.exists():
            shutil.copy2(str(best_model_path), 'models/fish_health_classifier.pt')
            print("✅ Model copied to: models/fish_health_classifier.pt")
        else:
            print(f"❌ Warning: Model file not found at {best_model_path}")
            print(f"   Searching for model in common locations...")
            
            # Try alternative paths
            possible_paths = [
                Path('runs/classify/fish_health/weights/best.pt'),
                Path.home() / 'runs/classify/fish_health/weights/best.pt',
                Path('C:/Users') / os.getlogin() / 'runs/classify/fish_health/weights/best.pt'
            ]
            
            for path in possible_paths:
                if path.exists():
                    print(f"   ✅ Found at: {path}")
                    shutil.copy2(str(path), 'models/fish_health_classifier.pt')
                    print("✅ Model copied to: models/fish_health_classifier.pt")
                    break
            else:
                raise FileNotFoundError(f"Could not find best.pt in any expected location")
        
        # Test on test set
        if test_dir.exists():
            print("\n🧪 Testing on test set...")
            test_results = model.val(data=str(data_path), split='test')
            print(f"\n📊 Test Results:")
            print(f"   Top-1 Accuracy: {test_results.top1:.2%}")
            print(f"   Top-5 Accuracy: {test_results.top5:.2%}")
        
        print("\n🎉 Training complete!")
        print("Next steps:")
        print("1. Run: python3 fish_health_detector.py (test the model)")
        print("2. Run: python3 main_with_health.py (full monitoring system)")
        
        return results
        
    except KeyboardInterrupt:
        print("\n⚠️ Training interrupted by user")
        print("Partial model may be saved in runs/classify/fish_health/")
    except Exception as e:
        print(f"\n❌ Training error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    parser = argparse.ArgumentParser(description='Train Fish Health Classification Model')
    parser.add_argument('--data', type=str, 
                       default='dataset/fish_health',
                       help='Path to dataset directory')
    parser.add_argument('--model', type=str, 
                       default='yolov8n-cls.pt',
                       help='YOLOv8 classification model')
    parser.add_argument('--epochs', type=int, default=50,
                       help='Number of training epochs')
    parser.add_argument('--imgsz', type=int, default=224,
                       help='Image size for training')
    parser.add_argument('--batch', type=int, default=16,
                       help='Batch size')
    parser.add_argument('--device', type=str, default='cpu',
                       help='Device (cpu or cuda)')
    
    args = parser.parse_args()
    train_fish_health_model(args)

if __name__ == "__main__":
    main()
