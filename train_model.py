#!/usr/bin/env python3
"""
YOLOv8 Fish Detection Model Training Script
Trains a custom YOLOv8 model on your fish dataset
"""

import argparse
import os
import sys
import yaml
from pathlib import Path

try:
    from ultralytics import YOLO
except ImportError:
    print("ERROR: ultralytics not installed")
    print("Install: pip install ultralytics")
    sys.exit(1)


def validate_dataset(data_yaml):
    """Validate dataset structure and configuration"""
    print("\n" + "=" * 60)
    print("Validating Dataset...")
    print("=" * 60)
    
    if not os.path.exists(data_yaml):
        print(f"❌ Dataset config not found: {data_yaml}")
        return False
    
    with open(data_yaml, 'r') as f:
        data = yaml.safe_load(f)
    
    # Check required fields
    required = ['train', 'val', 'names', 'nc']
    for field in required:
        if field not in data:
            print(f"❌ Missing field in {data_yaml}: {field}")
            return False
    
    # Check paths
    base_path = data.get('path', os.path.dirname(data_yaml))
    train_path = os.path.join(base_path, data['train'])
    val_path = os.path.join(base_path, data['val'])
    
    if not os.path.exists(train_path):
        print(f"❌ Training images not found: {train_path}")
        return False
    
    if not os.path.exists(val_path):
        print(f"❌ Validation images not found: {val_path}")
        return False
    
    # Count images
    train_images = len([f for f in os.listdir(train_path) if f.endswith(('.jpg', '.jpeg', '.png'))])
    val_images = len([f for f in os.listdir(val_path) if f.endswith(('.jpg', '.jpeg', '.png'))])
    
    print(f"✓ Dataset config: {data_yaml}")
    print(f"✓ Classes: {data['nc']} ({', '.join(data['names'].values() if isinstance(data['names'], dict) else data['names'])})")
    print(f"✓ Training images: {train_images}")
    print(f"✓ Validation images: {val_images}")
    
    if train_images < 50:
        print(f"⚠️  Warning: Only {train_images} training images (recommend 200+)")
    
    if val_images < 10:
        print(f"⚠️  Warning: Only {val_images} validation images (recommend 30+)")
    
    return True


def train_fish_model(args):
    """Train YOLOv8 model"""
    
    print("\n" + "=" * 60)
    print("YOLOv8 Fish Detection Training")
    print("=" * 60)
    print(f"Model: {args.model}")
    print(f"Dataset: {args.data}")
    print(f"Epochs: {args.epochs}")
    print(f"Batch size: {args.batch}")
    print(f"Image size: {args.imgsz}")
    print(f"Device: {args.device}")
    print("=" * 60)
    
    # Validate dataset
    if not validate_dataset(args.data):
        print("\n❌ Dataset validation failed!")
        return
    
    # Load model
    print(f"\n📦 Loading model: {args.model}")
    model = YOLO(args.model)
    
    # Train
    print(f"\n🚀 Starting training...")
    print("This may take several hours on Raspberry Pi 4")
    print("Press Ctrl+C to stop training early\n")
    
    try:
        results = model.train(
            data=args.data,
            epochs=args.epochs,
            batch=args.batch,
            imgsz=args.imgsz,
            device=args.device,
            project=args.project,
            name=args.name,
            exist_ok=True,
            pretrained=True,
            optimizer='Adam',
            verbose=True,
            patience=20,  # Early stopping
            save=True,
            plots=True
        )
        
        print("\n" + "=" * 60)
        print("✓ Training Complete!")
        print("=" * 60)
        
        # Find best model
        project_path = Path(args.project) / args.name
        best_model = project_path / "weights" / "best.pt"
        last_model = project_path / "weights" / "last.pt"
        
        if best_model.exists():
            print(f"✓ Best model: {best_model}")
            
            # Copy to models directory
            models_dir = Path("models")
            models_dir.mkdir(exist_ok=True)
            
            import shutil
            dest = models_dir / "fish_detection.pt"
            shutil.copy(best_model, dest)
            print(f"✓ Copied to: {dest}")
            
            print("\n" + "=" * 60)
            print("Next Steps:")
            print("=" * 60)
            print("1. Test model: python3 test_detector.py")
            print("2. Run system: ./start.sh")
            print("3. Adjust CONFIDENCE_THRESHOLD in config.py if needed")
            print("=" * 60)
        
        if last_model.exists():
            print(f"✓ Last model: {last_model}")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Training interrupted by user")
        print("Partial model may be saved in:", Path(args.project) / args.name)
    
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Validate the model
    print("\nRunning validation...")
    metrics = model.val()
    
    print(f"\nValidation Results:")
    print(f"  mAP50: {metrics.box.map50:.4f}")
    print(f"  mAP50-95: {metrics.box.map:.4f}")
    
    # Export model
    model_path = 'models/fish_detection.pt'
    os.makedirs('models', exist_ok=True)
    
    print(f"\nSaving model to: {model_path}")
    model.save(model_path)
    
    print("\n✓ Model training and export completed!")
    print(f"\nUpdate config.py with:")
    print(f"  YOLO_MODEL_PATH = '{model_path}'")

def main():
    parser = argparse.ArgumentParser(description='Train YOLOv8 fish detection model')
    parser.add_argument('--data', type=str, required=True,
                       help='Path to dataset YAML file')
    parser.add_argument('--epochs', type=int, default=100,
                       help='Number of training epochs (default: 100)')
    parser.add_argument('--img-size', type=int, default=640,
                       help='Image size for training (default: 640)')
    parser.add_argument('--batch-size', type=int, default=16,
                       help='Batch size (default: 16)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.data):
        print(f"Error: Dataset file not found: {args.data}")
        print("\nCreate a dataset YAML file with this format:")
        print("""
# fish_dataset.yaml
path: /path/to/dataset
train: images/train
val: images/val
test: images/test

names:
  0: fish
  1: dead_fish  # optional
        """)
        return
    
    train_model(
        data_yaml=args.data,
        epochs=args.epochs,
        img_size=args.img_size,
        batch_size=args.batch_size
    )

if __name__ == "__main__":
    main()
