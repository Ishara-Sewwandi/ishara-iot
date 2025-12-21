#!/usr/bin/env python3
"""
Dataset Preparation Tool
Splits collected behavior dataset into train/val/test sets
Creates YAML configuration for YOLOv8 training
"""

import os
import shutil
import random
import yaml
from pathlib import Path
import argparse
import json


def prepare_behavior_dataset(input_dir, output_dir, train_ratio=0.7, val_ratio=0.2, test_ratio=0.1):
    """
    Organize collected dataset into train/val/test splits
    
    Args:
        input_dir: Directory with collected images/labels
        output_dir: Output directory for organized dataset
        train_ratio: Percentage for training (default 0.7)
        val_ratio: Percentage for validation (default 0.2)
        test_ratio: Percentage for testing (default 0.1)
    """
    
    print("=" * 70)
    print("Fish Behavior Dataset Preparation")
    print("=" * 70)
    
    # Validate ratios
    if abs(train_ratio + val_ratio + test_ratio - 1.0) > 0.001:
        print(f"ERROR: Ratios must sum to 1.0")
        print(f"Current: {train_ratio + val_ratio + test_ratio}")
        return
    
    # Create output structure
    for split in ['train', 'val', 'test']:
        os.makedirs(os.path.join(output_dir, 'images', split), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'labels', split), exist_ok=True)
    
    # Get list of images
    images_dir = os.path.join(input_dir, 'images')
    labels_dir = os.path.join(input_dir, 'labels')
    
    if not os.path.exists(images_dir):
        print(f"ERROR: Images directory not found: {images_dir}")
        return
    
    # Find all image-label pairs
    image_files = [f for f in os.listdir(images_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    pairs = []
    for img_file in image_files:
        label_file = os.path.splitext(img_file)[0] + '.txt'
        label_path = os.path.join(labels_dir, label_file)
        
        if os.path.exists(label_path):
            pairs.append((img_file, label_file))
        else:
            print(f"⚠️  Warning: No label for {img_file}, skipping")
    
    if not pairs:
        print("ERROR: No valid image-label pairs found!")
        return
    
    print(f"\n✓ Found {len(pairs)} valid image-label pairs")
    
    # Shuffle and split
    random.shuffle(pairs)
    
    n_train = int(len(pairs) * train_ratio)
    n_val = int(len(pairs) * val_ratio)
    
    train_pairs = pairs[:n_train]
    val_pairs = pairs[n_train:n_train + n_val]
    test_pairs = pairs[n_train + n_val:]
    
    print(f"\nSplit:")
    print(f"  Training:   {len(train_pairs)} images ({len(train_pairs)/len(pairs)*100:.1f}%)")
    print(f"  Validation: {len(val_pairs)} images ({len(val_pairs)/len(pairs)*100:.1f}%)")
    print(f"  Test:       {len(test_pairs)} images ({len(test_pairs)/len(pairs)*100:.1f}%)")
    
    # Copy files
    def copy_split(pairs, split_name):
        print(f"\nCopying {split_name} set...")
        for img_file, label_file in pairs:
            # Copy image
            src_img = os.path.join(images_dir, img_file)
            dst_img = os.path.join(output_dir, 'images', split_name, img_file)
            shutil.copy2(src_img, dst_img)
            
            # Copy label
            src_label = os.path.join(labels_dir, label_file)
            dst_label = os.path.join(output_dir, 'labels', split_name, label_file)
            shutil.copy2(src_label, dst_label)
        
        print(f"✓ Copied {len(pairs)} pairs to {split_name}/")
    
    copy_split(train_pairs, 'train')
    copy_split(val_pairs, 'val')
    if test_pairs:
        copy_split(test_pairs, 'test')
    
    # Count behaviors
    behavior_counts = {}
    
    for split_name, split_pairs in [('train', train_pairs), ('val', val_pairs), ('test', test_pairs)]:
        for _, label_file in split_pairs:
            label_path = os.path.join(output_dir, 'labels', split_name, label_file)
            with open(label_path, 'r') as f:
                for line in f:
                    class_id = int(line.split()[0])
                    behavior_counts[class_id] = behavior_counts.get(class_id, 0) + 1
    
    # Create YAML config
    behavior_names = {
        0: 'healthy',
        1: 'fins_not_moving',
        2: 'side_floating',
        3: 'dead',
        4: 'normal_floating',
        5: 'lethargic'
    }
    
    # Filter to only classes present in dataset
    active_classes = {k: v for k, v in behavior_names.items() if k in behavior_counts}
    
    yaml_config = {
        'path': str(Path(output_dir).absolute()),
        'train': 'images/train',
        'val': 'images/val',
        'test': 'images/test' if test_pairs else None,
        'nc': len(active_classes),
        'names': active_classes
    }
    
    # Remove None values
    yaml_config = {k: v for k, v in yaml_config.items() if v is not None}
    
    yaml_path = os.path.join(output_dir, 'fish_behavior.yaml')
    with open(yaml_path, 'w') as f:
        yaml.dump(yaml_config, f, default_flow_style=False, sort_keys=False)
    
    print(f"\n✓ Created dataset config: {yaml_path}")
    
    # Create statistics file
    stats = {
        'total_images': len(pairs),
        'splits': {
            'train': len(train_pairs),
            'val': len(val_pairs),
            'test': len(test_pairs)
        },
        'behavior_counts': {behavior_names.get(k, f'class_{k}'): v 
                           for k, v in behavior_counts.items()},
        'classes': active_classes
    }
    
    stats_path = os.path.join(output_dir, 'dataset_stats.json')
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"✓ Created statistics: {stats_path}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("Dataset Preparation Complete!")
    print("=" * 70)
    print(f"\nDataset location: {output_dir}")
    print(f"Config file: {yaml_path}")
    print(f"\nBehavior distribution:")
    for class_id, count in sorted(behavior_counts.items()):
        behavior_name = behavior_names.get(class_id, f'class_{class_id}')
        print(f"  {behavior_name}: {count} instances")
    
    print("\n" + "=" * 70)
    print("Next Steps:")
    print("=" * 70)
    print(f"1. Review dataset in: {output_dir}")
    print(f"2. Train model:")
    print(f"   python3 train_model.py --data {yaml_path} --epochs 100 --batch 8 --imgsz 320")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description='Prepare fish behavior dataset for training')
    parser.add_argument('--input', type=str, default='dataset/behavior_data',
                       help='Input directory with collected data')
    parser.add_argument('--output', type=str, default='dataset/behavior_training',
                       help='Output directory for organized dataset')
    parser.add_argument('--train', type=float, default=0.7,
                       help='Training set ratio (default: 0.7)')
    parser.add_argument('--val', type=float, default=0.2,
                       help='Validation set ratio (default: 0.2)')
    parser.add_argument('--test', type=float, default=0.1,
                       help='Test set ratio (default: 0.1)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducibility')
    
    args = parser.parse_args()
    
    # Set random seed
    random.seed(args.seed)
    
    prepare_behavior_dataset(
        args.input,
        args.output,
        args.train,
        args.val,
        args.test
    )


if __name__ == "__main__":
    main()
