"""
Reorganize Fish Health Dataset - 6 Classes to 3 Classes
========================================================

OLD: bacterial, dead, fungal, healthy, parasitic, white_tail (6 classes)
NEW: dead, healthy, unhealthy (3 classes)

This script will:
1. Keep 'dead' and 'healthy' folders as-is
2. Create 'unhealthy' folder
3. Move bacterial, fungal, parasitic, white_tail → unhealthy
"""

import os
import shutil
from pathlib import Path


def reorganize_dataset(dataset_path="dataset/fish_health"):
    """Reorganize dataset from 6 to 3 classes"""
    
    dataset_path = Path(dataset_path)
    
    print("\n" + "=" * 60)
    print("Fish Health Dataset Reorganization")
    print("6 Classes → 3 Classes")
    print("=" * 60)
    
    # Process each split (train, val, test)
    for split in ['train', 'val', 'test']:
        split_path = dataset_path / split
        
        if not split_path.exists():
            print(f"\n⚠️ {split} directory not found, skipping...")
            continue
        
        print(f"\n📂 Processing {split.upper()}...")
        
        # Create unhealthy folder if it doesn't exist
        unhealthy_path = split_path / 'unhealthy'
        unhealthy_path.mkdir(exist_ok=True)
        
        # Classes to merge into unhealthy
        disease_classes = ['bacterial', 'fungal', 'parasitic', 'white_tail']
        
        for disease in disease_classes:
            disease_path = split_path / disease
            
            if disease_path.exists() and disease_path.is_dir():
                # Get all images in this disease folder
                images = list(disease_path.glob('*.jpg')) + list(disease_path.glob('*.png'))
                
                print(f"   Moving {len(images)} images from '{disease}' to 'unhealthy'...")
                
                # Move images
                for img in images:
                    # Create unique filename to avoid conflicts
                    new_name = f"{disease}_{img.name}"
                    dest = unhealthy_path / new_name
                    
                    shutil.move(str(img), str(dest))
                
                # Remove empty disease folder
                try:
                    disease_path.rmdir()
                    print(f"   ✓ Removed empty '{disease}' folder")
                except:
                    print(f"   ⚠️ Could not remove '{disease}' folder (may not be empty)")
        
        # Count final distribution
        print(f"\n   Final class distribution for {split}:")
        for class_name in ['dead', 'healthy', 'unhealthy']:
            class_path = split_path / class_name
            if class_path.exists():
                count = len(list(class_path.glob('*.jpg')) + list(class_path.glob('*.png')))
                print(f"     {class_name}: {count} images")
    
    print("\n" + "=" * 60)
    print("✅ Dataset reorganization complete!")
    print("=" * 60)
    print("\nNew structure:")
    print("  - dead: Fish that are dead")
    print("  - healthy: Fish with no visible diseases")
    print("  - unhealthy: Fish with any disease (bacterial, fungal, parasitic, white_tail)")
    print("\nNext step: Train the model")
    print("  python train_fish_health_classifier.py --data dataset/fish_health --epochs 100")


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║     DATASET REORGANIZATION: 6 → 3 CLASSES                  ║
╚════════════════════════════════════════════════════════════╝

This will merge disease classes into a single 'unhealthy' class:
  • bacterial    ┐
  • fungal       │
  • parasitic    ├─→ unhealthy
  • white_tail   ┘
  
  • dead         → dead (unchanged)
  • healthy      → healthy (unchanged)

⚠️ WARNING: This will MOVE (not copy) image files!
⚠️ Make a backup first if you want to keep the original structure.

""")
    
    confirm = input("Continue? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        reorganize_dataset()
    else:
        print("\nCancelled. No changes made.")
