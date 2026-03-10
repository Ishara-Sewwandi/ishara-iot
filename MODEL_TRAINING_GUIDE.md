# 🐟 Fish Detection & Health Classification — Model Training Guide

## Overview

This project uses **two YOLOv8 models** that work together in the live stream:

| Model | Type | File | Purpose |
|-------|------|------|---------|
| **Fish Detection** | YOLOv8n (Object Detection) | `models/fish_detection.pt` | Draws bounding boxes around fish in the frame |
| **Fish Health Classifier** | YOLOv8n-cls (Classification) | `models/fish_health_classifier.pt` | Classifies each detected fish as `healthy`, `unhealthy`, or `dead` |

### How They Work Together

```
Camera Frame
    │
    ▼
┌──────────────────────┐
│  Fish Detection Model │  ← Finds all fish, outputs bounding boxes
│  (models/fish_detection.pt)
└──────────┬───────────┘
           │ For each detected fish...
           ▼
┌──────────────────────────┐
│  Fish Health Classifier   │  ← Crops each fish, classifies health
│  (models/fish_health_classifier.pt)
└──────────┬───────────────┘
           │
           ▼
    Annotated Frame → ffmpeg → MediaMTX → HLS → Frontend
```

---

## 📋 Training on Your Laptop (NOT on Raspberry Pi)

> **Important:** Train on your laptop/PC with a GPU for much faster training.
> After training, transfer the `.pt` model files to the Raspberry Pi via Git.

### Requirements for Laptop

- Python 3.9+ 
- NVIDIA GPU recommended (CUDA) — CPU works but is 10-50x slower
- 8 GB+ RAM

### Install Dependencies on Laptop

```bash
# Clone the repo on your laptop
git clone https://github.com/Ishara-Sewwandi/ishara-iot.git
cd ishara-iot

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install training dependencies
pip install ultralytics opencv-python numpy pyyaml
```

---

## 🎯 Model 1: Fish Detection (Object Detection)

This model detects fish in video frames and draws bounding boxes.

### Dataset Structure

```
dataset/
└── fish_detection/
    ├── data.yaml              ← Dataset config file
    ├── images/
    │   ├── train/             ← Training images (.jpg/.png)
    │   │   ├── img001.jpg
    │   │   ├── img002.jpg
    │   │   └── ...
    │   ├── val/               ← Validation images (10-20% of total)
    │   │   ├── img101.jpg
    │   │   └── ...
    │   └── test/              ← Test images (optional, 10%)
    │       └── ...
    └── labels/
        ├── train/             ← YOLO format label files (.txt)
        │   ├── img001.txt
        │   ├── img002.txt
        │   └── ...
        ├── val/
        │   ├── img101.txt
        │   └── ...
        └── test/
            └── ...
```

### Label Format (YOLO .txt)

Each `.txt` file has one line per object:
```
<class_id> <x_center> <y_center> <width> <height>
```
All values are **normalized (0.0–1.0)** relative to image size.

**Example `img001.txt`:**
```
0 0.45 0.52 0.30 0.18
0 0.72 0.35 0.25 0.15
```
- `0` = class ID for "fish"
- Coordinates are center-x, center-y, width, height (normalized)

### How to Label Images

Use one of these free labeling tools:

| Tool | URL | Notes |
|------|-----|-------|
| **Roboflow** | https://roboflow.com | Web-based, can export YOLO format directly |
| **CVAT** | https://cvat.ai | Web-based, powerful |
| **LabelImg** | `pip install labelImg` | Desktop app, classic |
| **Label Studio** | https://labelstud.io | Web-based |

**With Roboflow (Recommended):**
1. Create free account at https://roboflow.com
2. Create new project → Object Detection
3. Upload your fish images
4. Draw bounding boxes around each fish
5. Export → Format: **YOLOv8** → Download zip
6. Extract into `dataset/fish_detection/`

### Create `data.yaml`

Create `dataset/fish_detection/data.yaml`:

```yaml
# Fish Detection Dataset
path: dataset/fish_detection  # dataset root (relative to project root)
train: images/train
val: images/val
test: images/test

# Classes
nc: 1  # number of classes
names:
  0: fish
```

**For multi-class detection** (e.g., live fish + dead fish):
```yaml
path: dataset/fish_detection
train: images/train
val: images/val
test: images/test

nc: 2
names:
  0: fish
  1: dead_fish
```

### Training Command

```bash
# Basic training (GPU)
python train_model.py --data dataset/fish_detection/data.yaml --epochs 100 --batch-size 16 --img-size 640

# If using GPU (recommended)
python train_model.py --data dataset/fish_detection/data.yaml --epochs 100 --batch-size 16 --img-size 640

# Lighter training (CPU or low VRAM)
python train_model.py --data dataset/fish_detection/data.yaml --epochs 50 --batch-size 8 --img-size 416
```

**Or use the Ultralytics CLI directly:**

```bash
# GPU (fastest)
yolo detect train data=dataset/fish_detection/data.yaml model=yolov8n.pt epochs=100 imgsz=640 batch=16 device=0

# CPU
yolo detect train data=dataset/fish_detection/data.yaml model=yolov8n.pt epochs=100 imgsz=640 batch=8 device=cpu
```

### Training Output

After training, the best model will be at:
```
runs/detect/train/weights/best.pt   ← Use this one
runs/detect/train/weights/last.pt   ← Checkpoint
```

The training script auto-copies `best.pt` → `models/fish_detection.pt`

### Recommended Dataset Size

| Quality | Train Images | Val Images | Notes |
|---------|-------------|------------|-------|
| Minimum | 100 | 20 | Basic detection |
| Good | 500 | 100 | Reliable detection |
| Best | 2000+ | 400+ | High accuracy |

> **Tip:** Include images from different angles, lighting, water clarity, and fish counts.

---

## 🏥 Model 2: Fish Health Classifier (Image Classification)

This model classifies cropped fish images into health categories.

### Current Classes (3-class system)

| Class | Description | Severity |
|-------|-------------|----------|
| `healthy` | Normal, active fish | 0 (Green) |
| `unhealthy` | Showing signs of disease | 2 (Orange) |
| `dead` | Dead or dying fish | 3 (Red) |

### Dataset Structure

```
dataset/
└── fish_health/
    ├── train/
    │   ├── healthy/           ← Healthy fish images
    │   │   ├── healthy_001.jpg
    │   │   ├── healthy_002.jpg
    │   │   └── ...
    │   ├── unhealthy/         ← Unhealthy/sick fish images
    │   │   ├── unhealthy_001.jpg
    │   │   └── ...
    │   └── dead/              ← Dead fish images
    │       ├── dead_001.jpg
    │       └── ...
    ├── val/
    │   ├── healthy/
    │   ├── unhealthy/
    │   └── dead/
    └── test/
        ├── healthy/
        ├── unhealthy/
        └── dead/
```

> **No YAML or label files needed!** YOLOv8 classification uses **folder names as class labels**.
> Just put images in the correct folders.

### Extended 6-Class System (Optional)

You already have a 6-class dataset in `dataset/Final_Dataset/`:

| Class | Current Count (train) |
|-------|-----------------------|
| `healthy` | 2291 |
| `dead` | 310 |
| `bacterial` | 227 |
| `fungal` | 73 |
| `parasitic` | 75 |
| `white_tail` | 138 |

To use 6 classes instead of 3, update `fish_health_detector.py`:
```python
self.class_names = ['bacterial', 'dead', 'fungal', 'healthy', 'parasitic', 'white_tail']
```
> **Note:** YOLOv8 sorts class names **alphabetically** by folder name.

### Training Command

```bash
# 3-class (dead/healthy/unhealthy)
python train_fish_health_classifier.py --data dataset/fish_health --epochs 50 --imgsz 224 --batch 16 --device cpu

# 6-class (bacterial/dead/fungal/healthy/parasitic/white_tail)
python train_fish_health_classifier.py --data dataset/Final_Dataset --epochs 50 --imgsz 224 --batch 16 --device cpu

# GPU (much faster)
python train_fish_health_classifier.py --data dataset/Final_Dataset --epochs 50 --imgsz 224 --batch 32 --device 0
```

**Or use the Ultralytics CLI:**

```bash
# 6-class with GPU
yolo classify train data=dataset/Final_Dataset model=yolov8n-cls.pt epochs=50 imgsz=224 batch=32 device=0

# 3-class with CPU
yolo classify train data=dataset/fish_health model=yolov8n-cls.pt epochs=50 imgsz=224 batch=16 device=cpu
```

### Training Output

```
runs/classify/fish_health/weights/best.pt   ← Use this one
```

The training script auto-copies `best.pt` → `models/fish_health_classifier.pt`

### Recommended Dataset Size (Per Class)

| Quality | Images/Class | Notes |
|---------|-------------|-------|
| Minimum | 50 | Basic classification |
| Good | 200 | Balanced, reliable |
| Best | 500+ | High accuracy |

> **Tip:** Try to keep classes **balanced**. If `healthy` has 2000 images, other classes should have at least 200-300.

---

## 🔄 Transfer Trained Models to Raspberry Pi

After training on your laptop, transfer the models to the Pi using Git.

### Method 1: Via Git (Recommended)

**On your laptop (after training):**

```bash
cd ishara-iot

# Make sure trained models are in the right location
ls models/fish_detection.pt
ls models/fish_health_classifier.pt

# Check if models are gitignored
git check-ignore models/fish_detection.pt

# If models are gitignored, you need to force add them
git add -f models/fish_detection.pt
git add -f models/fish_health_classifier.pt

# Commit and push
git commit -m "Updated trained models (fish detection + health classifier)"
git push origin testing
```

**On Raspberry Pi:**

```bash
cd ~/Documents/GitHub/ishara-iot

# Pull the updated models
git pull origin testing

# Verify models are updated
ls -la models/*.pt

# Restart the streaming service to use new models
sudo systemctl restart mediamtx-camera

# Check logs to confirm new models loaded
journalctl -u mediamtx-camera -n 20 --no-pager
```

### Method 2: Direct SCP Transfer

**From your laptop terminal (PowerShell on Windows):**

```powershell
# Transfer fish detection model
scp models/fish_detection.pt koi@192.168.8.101:~/Documents/GitHub/ishara-iot/models/

# Transfer health classifier model
scp models/fish_health_classifier.pt koi@192.168.8.101:~/Documents/GitHub/ishara-iot/models/
```

**Then on Raspberry Pi:**

```bash
# Restart service to use new models
sudo systemctl restart mediamtx-camera
journalctl -u mediamtx-camera -f
```

### Method 3: USB Drive

1. Copy `models/fish_detection.pt` and `models/fish_health_classifier.pt` to USB
2. Plug USB into Raspberry Pi
3. Copy files:
   ```bash
   cp /media/koi/USB/fish_detection.pt ~/Documents/GitHub/ishara-iot/models/
   cp /media/koi/USB/fish_health_classifier.pt ~/Documents/GitHub/ishara-iot/models/
   sudo systemctl restart mediamtx-camera
   ```

---

## 📊 Verify Models on Raspberry Pi

After transferring models, verify they work:

```bash
cd ~/Documents/GitHub/ishara-iot
source venv/bin/activate

# Test fish detection model
python3 test_detector.py

# Test health classifier
python3 -c "
from fish_health_detector import FishHealthDetector
detector = FishHealthDetector()
print('Model loaded:', detector.model_available)
print('Classes:', detector.class_names)
"

# Test on a sample image
python3 test_my_images.py

# Check live stream is working with new models
sudo systemctl restart mediamtx-camera
journalctl -u mediamtx-camera -f
```

---

## 🧪 Full Training Workflow (Step by Step)

### Step 1: Prepare Dataset on Laptop

```
ishara-iot/
├── dataset/
│   ├── fish_detection/          ← For Model 1
│   │   ├── data.yaml
│   │   ├── images/
│   │   │   ├── train/   (your fish photos)
│   │   │   └── val/     (10-20% for validation)
│   │   └── labels/
│   │       ├── train/   (YOLO .txt labels)
│   │       └── val/
│   │
│   └── Final_Dataset/           ← For Model 2 (6-class)
│       ├── train/
│       │   ├── healthy/
│       │   ├── dead/
│       │   ├── bacterial/
│       │   ├── fungal/
│       │   ├── parasitic/
│       │   └── white_tail/
│       ├── val/
│       └── test/
```

### Step 2: Train Fish Detection Model

```bash
cd ishara-iot
source venv/bin/activate   # or venv\Scripts\activate on Windows

# Train (GPU recommended)
python train_model.py \
    --data dataset/fish_detection/data.yaml \
    --epochs 100 \
    --batch-size 16 \
    --img-size 640

# Result → models/fish_detection.pt
```

### Step 3: Train Health Classifier

```bash
# Train 6-class model
python train_fish_health_classifier.py \
    --data dataset/Final_Dataset \
    --epochs 50 \
    --imgsz 224 \
    --batch 32 \
    --device 0

# Result → models/fish_health_classifier.pt
```

### Step 4: Push Models to Git

```bash
git add -f models/fish_detection.pt models/fish_health_classifier.pt
git commit -m "Retrained models with new dataset"
git push origin testing
```

### Step 5: Pull on Raspberry Pi

```bash
ssh koi@192.168.8.101
cd ~/Documents/GitHub/ishara-iot
git pull origin testing
sudo systemctl restart mediamtx-camera
journalctl -u mediamtx-camera -f
```

---

## ⚙️ Config Tuning (on Raspberry Pi)

After deploying new models, you may need to adjust thresholds in `config.py`:

```python
# config.py — Key settings to tune

CONFIDENCE_THRESHOLD = 0.25    # Detection confidence (lower = more detections, more false positives)
IOU_THRESHOLD = 0.4            # Overlap threshold for NMS
YOLO_IMG_SIZE = 416            # Detection input size (320=fast, 640=accurate)
YOLO_MAX_DET = 20              # Max detections per frame
```

And in `fish_health_detector.py`:
```python
confidence_threshold = 0.65    # Health classification confidence
                               # Higher (0.75+) = fewer but more reliable predictions
                               # Lower (0.50)  = more predictions but less reliable
```

---

## 🔍 Troubleshooting

### Training fails with "CUDA out of memory"
- Reduce `--batch-size` (try 8 or 4)
- Reduce `--img-size` (try 416 or 320)
- Use `--device cpu` (slower but no VRAM limit)

### Model not detecting fish after retrain
- Check `CONFIDENCE_THRESHOLD` in `config.py` — try lowering to `0.15`
- Verify the `data.yaml` class names match your labels
- Ensure enough training images (200+ recommended)

### Health classifier always says "uncertain"
- The `confidence_threshold` in `fish_health_detector.py` may be too high
- Try lowering to `0.50`
- Ensure balanced dataset (similar image counts per class)

### "Permission denied" when pushing models to Git
```bash
# Models might be in .gitignore — force add
git add -f models/fish_detection.pt
git add -f models/fish_health_classifier.pt
```

### Model file too large for Git (>100MB)
- YOLOv8n models are ~6MB, YOLOv8s ~22MB — should be fine
- If using larger models (YOLOv8m/l/x), use Git LFS:
  ```bash
  git lfs install
  git lfs track "*.pt"
  git add .gitattributes
  git add -f models/*.pt
  git commit -m "Add models with LFS"
  git push
  ```

---

## 📝 Quick Reference

| Task | Command |
|------|---------|
| Train fish detection | `python train_model.py --data dataset/fish_detection/data.yaml --epochs 100` |
| Train health classifier (3-class) | `python train_fish_health_classifier.py --data dataset/fish_health --epochs 50` |
| Train health classifier (6-class) | `python train_fish_health_classifier.py --data dataset/Final_Dataset --epochs 50` |
| Push models to Git | `git add -f models/*.pt && git commit -m "Updated models" && git push` |
| Pull models on Pi | `git pull origin testing` |
| Restart stream with new models | `sudo systemctl restart mediamtx-camera` |
| Check stream logs | `journalctl -u mediamtx-camera -f` |
| Test detection model | `python3 test_detector.py` |
| Check HLS stream | `curl https://mediamtx.koifishfriend.online/live/camera/index.m3u8` |

---

## 📌 Model Files Summary

| File | Size | Type | Classes |
|------|------|------|---------|
| `models/fish_detection.pt` | ~6 MB | YOLOv8n detection | `fish` |
| `models/fish_health_classifier.pt` | ~3 MB | YOLOv8n-cls classification | `dead`, `healthy`, `unhealthy` |
| `yolov8n.pt` | ~6 MB | Pre-trained base (detection) | COCO 80 classes |
| `yolov8n-cls.pt` | ~3 MB | Pre-trained base (classification) | ImageNet 1000 classes |
