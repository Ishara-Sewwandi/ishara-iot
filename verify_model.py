#!/usr/bin/env python3
"""
Verify if fish_health_classifier.pt is trained
"""

from ultralytics import YOLO
import os

model_path = 'models/fish_health_classifier.pt'

if not os.path.exists(model_path):
    print(f"❌ Model not found: {model_path}")
    exit(1)

print("Loading model...")
model = YOLO(model_path)

print("\n" + "="*60)
print("Model Information")
print("="*60)

# Check if it's a classification model
print(f"Task: {model.task}")
print(f"Model type: {type(model.model).__name__}")

# Get model names/classes
if hasattr(model, 'names') and model.names:
    print(f"\nNumber of classes: {len(model.names)}")
    print(f"Classes: {model.names}")
else:
    print("\n⚠️ No class names found")

# Check model parameters
try:
    import torch
    checkpoint = torch.load(model_path, map_location='cpu')
    
    if 'train_args' in checkpoint:
        print("\n" + "="*60)
        print("Training Arguments Found")
        print("="*60)
        for key, val in checkpoint['train_args'].items():
            print(f"{key}: {val}")
    
    if 'epoch' in checkpoint:
        print(f"\n✅ Model was trained for {checkpoint['epoch']} epochs")
    
    if 'model' in checkpoint:
        print("✅ Model weights present")
        
except Exception as e:
    print(f"\n⚠️ Could not load checkpoint details: {e}")

print("\n" + "="*60)
print("Conclusion")
print("="*60)

# Compare with base model
base_model_path = 'yolov8n-cls.pt'
if os.path.exists(base_model_path):
    model_size = os.path.getsize(model_path)
    base_size = os.path.getsize(base_model_path)
    
    print(f"Custom model size: {model_size / 1024 / 1024:.2f} MB")
    print(f"Base model size: {base_size / 1024 / 1024:.2f} MB")
    
    if model.names and len(model.names) == 6:
        print("\n✅ Model appears to be TRAINED")
        print("   - Has 6 custom classes (bacterial, dead, fungal, healthy, parasitic, white_tail)")
    elif model_size == base_size:
        print("\n⚠️ Model appears to be UNTRAINED (same size as base model)")
    else:
        print("\n⚠️ Model status UNCLEAR")
else:
    print("\nBase model not found for comparison")
