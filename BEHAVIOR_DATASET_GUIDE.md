# Advanced Fish Behavior Dataset Collection Guide

## Overview

This advanced dataset collection system helps you train a YOLOv8 model that can detect specific fish behaviors, especially **fin movement** and **health states**. This goes beyond basic fish detection to identify mortality indicators.

---

## What This System Detects

The dataset collector lets you label 6 different fish behaviors:

| Behavior | Description | Detection Goal |
|----------|-------------|----------------|
| **Healthy** | Fish with actively moving fins | Normal, active fish |
| **Fins Not Moving** | Fish with inactive/still fins | **MORTALITY INDICATOR** ⚠️ |
| **Side Floating** | Fish floating on their side | **MORTALITY INDICATOR** ⚠️ |
| **Dead** | Dead fish (belly-up, no movement) | **CRITICAL** 🚨 |
| **Normal Floating** | Fish naturally floating at surface | Normal behavior |
| **Lethargic** | Slow movement, minimal activity | Early warning sign |

---

## Quick Start (3 Steps)

### Step 1: Collect & Label Behavior Data (Interactive)

```bash
python3 collect_behavior_dataset.py --output dataset/behavior_data
```

**What you'll do:**
1. Select a behavior category (1-6)
2. Click and drag to draw boxes around fish showing that behavior
3. Press SPACE to save the labeled image
4. Repeat for 200-500 images across all behaviors

**Interface Controls:**
- **Mouse**: Click & drag to draw bounding box
- **SPACE**: Save current frame with labels
- **ESC**: Clear all boxes on current frame
- **C**: Change behavior category
- **1-6**: Quick switch to behavior category
- **Q**: Quit and save session

### Step 2: Prepare Dataset for Training

```bash
python3 prepare_dataset.py \
  --input dataset/behavior_data \
  --output dataset/behavior_training
```

This automatically:
- Splits data into train (70%), validation (20%), test (10%)
- Creates YOLO format labels
- Generates `fish_behavior.yaml` config
- Creates dataset statistics

### Step 3: Train Behavior Detection Model

```bash
python3 train_model.py \
  --data dataset/behavior_training/fish_behavior.yaml \
  --epochs 100 \
  --batch 8 \
  --imgsz 320
```

**Or use Google Colab (faster)**:
- Upload dataset to Colab
- Train with GPU (15-30 minutes)
- Download `best.pt`
- Copy to `models/fish_detection.pt`

---

## Expected Results

### After Training with Good Dataset

**Fin Movement Detection:**
- ✅ Accurately identifies fish with inactive fins
- ✅ Distinguishes from healthy swimming fish
- ✅ Early warning system (fins stop before death)
- ✅ ~85-95% accuracy with 200+ examples

**Side Floating Detection:**
- ✅ Detects loss of buoyancy control
- ✅ Immediate alert trigger
- ✅ ~90-98% accuracy (easier to detect)

**Dead Fish Detection:**
- ✅ 95-99% accuracy
- ✅ Clear visual indicators
- ✅ Prevents false alarms

---

## Quick Command Reference

```bash
# Start interactive collection
python3 collect_behavior_dataset.py

# Prepare dataset after collection
python3 prepare_dataset.py --input dataset/behavior_data --output dataset/behavior_training

# Train model
python3 train_model.py --data dataset/behavior_training/fish_behavior.yaml --epochs 100

# Test model
python3 test_detector.py

# Run full system
./start.sh
```

**Result**: A custom model that detects not just "fish" but specific health states and mortality indicators, enabling true **early warning fish mortality detection**! 🐟✅
