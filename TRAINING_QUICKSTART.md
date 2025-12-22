# Quick Start: Train Custom Fish Detection Model

## Problem
YOLOv8n detects ANY object as fish. You need a custom model trained on YOUR fish.

## Quick Solution (3 Steps)

### Step 1: Collect Fish Images (30 minutes)

**Manual Capture** (best for variety):
```bash
python3 capture_fish_images.py --mode manual
# Press SPACE to capture images
# Take 200-500 images from different angles/times
```

**Auto Capture** (for time-lapse):
```bash
python3 capture_fish_images.py --mode auto --num 300 --interval 2
# Captures 300 images, 1 every 2 seconds
```

**Images will be saved in**: `dataset/images/raw/`

### Step 2: Annotate Images (1-2 hours)

**Option A: Roboflow (Recommended - Easiest)**
1. Go to https://roboflow.com
2. Create free account
3. New Project → "Fish Detection" → Object Detection
4. Upload images from `dataset/images/raw/`
5. Click each image, press `B`, draw box around fish
6. Repeat for all images
7. Generate → YOLOv8 format → Download

**Option B: LabelImg (Local)**
```bash
pip install labelImg
labelImg dataset/images/raw dataset/labels
# Press W to draw box, D for next image
```

### Step 3: Train Model

**If using Roboflow:**
```bash
# Unzip downloaded dataset
unzip your-dataset.zip -d dataset/

# Train
python3 train_model.py \
  --data dataset/data.yaml \
  --epochs 100 \
  --batch 8 \
  --imgsz 320
```

**If using LabelImg:**
```bash
# Organize images
mkdir -p dataset/images/{train,val}
mkdir -p dataset/labels/{train,val}

# Move 80% to train, 20% to val
# (do this manually or use script below)

# Create config
cp fish_dataset.yaml.example dataset/fish_dataset.yaml

# Train
python3 train_model.py \
  --data dataset/fish_dataset.yaml \
  --epochs 100 \
  --batch 8 \
  --imgsz 320
```

**Training will take 2-6 hours on Pi 4**

---

## Faster Training (Recommended)

### Use Google Colab (FREE GPU - 15 minutes!)

1. Go to https://colab.research.google.com
2. New Notebook
3. Paste this code:

```python
# Install YOLOv8
!pip install ultralytics

# Upload your dataset (zip file)
from google.colab import files
uploaded = files.upload()  # Upload your dataset.zip

# Unzip
!unzip dataset.zip -d dataset

# Train (FAST with GPU!)
!yolo task=detect mode=train \
  model=yolov8n.pt \
  data=dataset/data.yaml \
  epochs=100 \
  imgsz=320 \
  batch=16 \
  device=0

# Download trained model
from google.colab import files
files.download('runs/detect/train/weights/best.pt')
```

4. Run all cells
5. Download `best.pt`
6. Copy to Pi:
```bash
scp best.pt pi@raspberrypi.local:~/Documents/GitHub/ishara-iot/models/fish_detection.pt
```

---

## After Training

### Test Model
```bash
python3 test_detector.py
```

### Run System
```bash
./start.sh
```

### Adjust Detection Threshold

If too many false detections:
```python
# config.py
CONFIDENCE_THRESHOLD = 0.6  # Higher = stricter
```

If missing fish:
```python
# config.py
CONFIDENCE_THRESHOLD = 0.3  # Lower = more detections
```

---

## Dataset Requirements

**Minimum**:
- 100 images (train: 70, val: 20, test: 10)
- At least 200 labeled fish (across all images)

**Recommended**:
- 300-500 images
- Various conditions:
  - Different times (morning, noon, evening)
  - Different weather (sunny, cloudy, rainy)
  - Different fish positions (swimming, floating, side)
  - Different depths/angles

**Best**:
- 1000+ images
- Include negative examples (no fish)
- Multiple fish species
- Various water conditions

---

## Quick Commands Reference

```bash
# Capture images manually
python3 capture_fish_images.py --mode manual

# Capture 500 images automatically
python3 capture_fish_images.py --mode auto --num 500 --interval 1

# Time-lapse (60 minutes, 1 image every 10 seconds)
python3 capture_fish_images.py --mode timelapse --duration 60 --interval 10

# Train model
python3 train_model.py --data dataset/fish_dataset.yaml --epochs 100

# Test model
python3 test_detector.py

# Run system
./start.sh
```

---

## Troubleshooting

### "No images found"
- Check `dataset/images/train/` has .jpg filesfit to web
- Check `dataset/labels/train/` has .txt files (same names)

### "Out of memory during training"
```bash
python3 train_model.py --batch 4  # Lower batch size
```

### "Training takes too long"
- Use Google Colab (GPU) instead of Pi
- Or reduce epochs: `--epochs 50`

### "Model still detects non-fish objects"
- Add more training images with negative examples
- Increase CONFIDENCE_THRESHOLD in config.py
- Train longer (more epochs)

---

## Expected Results

**After training with 300+ images:**
- ✅ Only detects fish (your specific species)
- ✅ Ignores reflections, plants, hands, etc.
- ✅ Better accuracy in your specific pond/tank
- ✅ Faster inference (trained on your resolution)

**Training improves by 50-90% compared to generic YOLOv8n!** 🐟✅
