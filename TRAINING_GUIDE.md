# YOLOv8 Training Guide for Fish Detection

## Problem
The current model (YOLOv8n pretrained) detects **any object** as a fish because it wasn't trained specifically for fish detection.

## Solution
Train a **custom YOLOv8 model** on fish images to recognize only fish.

---

## Step 1: Prepare Your Fish Dataset

### A. Collect Fish Images

You need **200-1000+ images** of fish in your specific pond/tank:

**Image Requirements:**
- Various angles (top-down, side view)
- Different lighting conditions (day, night, cloudy)
- Different fish positions (swimming, floating, side-floating)
- Various fish sizes and types in your pond
- Include negative examples (water, plants, reflections)

**How to Collect:**
```bash
# Use your Pi Camera to capture images
cd /home/koi/Documents/GitHub/ishara-iot

# Create dataset directory
mkdir -p dataset/images

# Capture images manually
python3 -c "
from camera_handler import CameraHandler
from config import Config
import cv2
import time

config = Config()
camera = CameraHandler(config)
camera.start()

print('Press SPACE to capture, Q to quit')
count = 0

while True:
    frame = camera.capture_frame()
    if frame is not None:
        cv2.imshow('Capture Fish Images', frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord(' '):
        filename = f'dataset/images/fish_{count:04d}.jpg'
        cv2.imwrite(filename, frame)
        print(f'Saved: {filename}')
        count += 1
    elif key == ord('q'):
        break

camera.stop()
cv2.destroyAllWindows()
"
```

### B. Annotate Images (Label Fish)

You need to draw bounding boxes around fish in each image.

**Option 1: LabelImg (Recommended)**
```bash
# Install LabelImg
pip install labelImg

# Run LabelImg
labelImg dataset/images dataset/labels

# Instructions:
# 1. Open each image
# 2. Press 'W' to draw bounding box
# 3. Draw box around each fish
# 4. Label it as "fish"
# 5. Press 'D' for next image
# 6. Save as YOLO format
```

**Option 2: Roboflow (Online - Easier)**
1. Go to https://roboflow.com (free account)
2. Create new project: "Fish Detection"
3. Upload your images
4. Annotate online (draw boxes around fish)
5. Export as "YOLOv8" format
6. Download zip file

**Option 3: CVAT (Online - Free)**
1. Go to https://app.cvat.ai
2. Create project and task
3. Upload images
4. Annotate with bounding boxes
5. Export as "YOLO 1.1" format

### C. Dataset Structure

Your dataset should look like this:
```
dataset/
├── images/
│   ├── train/
│   │   ├── fish_0001.jpg
│   │   ├── fish_0002.jpg
│   │   └── ...
│   ├── val/
│   │   ├── fish_0101.jpg
│   │   ├── fish_0102.jpg
│   │   └── ...
│   └── test/
│       ├── fish_0201.jpg
│       └── ...
└── labels/
    ├── train/
    │   ├── fish_0001.txt
    │   ├── fish_0002.txt
    │   └── ...
    ├── val/
    │   ├── fish_0101.txt
    │   └── ...
    └── test/
        ├── fish_0201.txt
        └── ...
```

**Split ratio:**
- Training: 70-80% of images
- Validation: 10-15% of images
- Test: 10-15% of images

### D. Label Format (YOLO)

Each `.txt` file contains bounding boxes:
```
class_id center_x center_y width height
```

Example `fish_0001.txt`:
```
0 0.5123 0.4567 0.3245 0.2891
0 0.7234 0.6123 0.2456 0.1892
```

Where:
- `0` = class ID (0 for "fish")
- All coordinates are normalized (0-1)

---

## Step 2: Create Dataset Configuration

Create `fish_dataset.yaml`:

```yaml
# Fish Detection Dataset Configuration

# Dataset paths (relative to this file or absolute)
path: /home/koi/Documents/GitHub/ishara-iot/dataset
train: images/train
val: images/val
test: images/test

# Classes
names:
  0: fish

# Number of classes
nc: 1
```

Save this as `/home/koi/Documents/GitHub/ishara-iot/dataset/fish_dataset.yaml`

---

## Step 3: Train YOLOv8 Model

### A. Using the Training Script

```bash
cd /home/koi/Documents/GitHub/ishara-iot

# Activate virtual environment
source venv/bin/activate

# Run training (this will take 2-6 hours on Pi 4)
python3 train_model.py \
  --data dataset/fish_dataset.yaml \
  --epochs 100 \
  --batch 8 \
  --imgsz 320 \
  --model yolov8n.pt
```

**Training Parameters Explained:**
- `--epochs 100`: Train for 100 iterations (more = better, but longer)
- `--batch 8`: Process 8 images at once (lower if out of memory)
- `--imgsz 320`: Image size 320x320 (faster on Pi 4)
- `--model yolov8n.pt`: Start from pretrained YOLOv8 nano model

### B. Monitor Training

The script will show:
```
Epoch    GPU_mem    box_loss    cls_loss    dfl_loss    Instances    Size
1/100    0.00G      1.234       0.567       1.234       42          320
2/100    0.00G      1.123       0.456       1.123       42          320
...
```

**What to watch:**
- `box_loss`: Bounding box accuracy (should decrease)
- `cls_loss`: Classification accuracy (should decrease)
- Lower values = better model

### C. Training on More Powerful Computer (Recommended)

**Pi 4 is SLOW for training** (2-6 hours). Better to train on:

**Option 1: Your Laptop/Desktop**
```bash
# Install Python and requirements
pip install ultralytics torch torchvision

# Copy dataset to your computer
# Train there (much faster with GPU)
yolo task=detect mode=train \
  model=yolov8n.pt \
  data=fish_dataset.yaml \
  epochs=100 \
  imgsz=320 \
  batch=16

# Copy trained model back to Pi
scp runs/detect/train/weights/best.pt pi@raspberrypi:/home/koi/Documents/GitHub/ishara-iot/models/fish_detection.pt
```

**Option 2: Google Colab (Free GPU)**
1. Go to https://colab.research.google.com
2. Create new notebook
3. Use the training code (see below)
4. Download trained model
5. Copy to Pi

**Option 3: Roboflow (Automated)**
1. Upload dataset to Roboflow
2. Click "Train" → "YOLOv8"
3. Wait 10-30 minutes
4. Download trained model
5. Copy to Pi

---

## Step 4: Use Trained Model

### A. Copy Model to Project

```bash
# After training, copy the best model
cp runs/detect/train/weights/best.pt models/fish_detection.pt
```

### B. Update Configuration

The system will automatically use `models/fish_detection.pt` if it exists!

Check `config.py`:
```python
YOLO_MODEL_PATH = "models/fish_detection.pt"  # Already configured
```

### C. Test Model

```bash
# Test the trained model
python3 test_detector.py
```

---

## Step 5: Improve Model Performance

### If Model Misses Fish:
1. **Lower confidence threshold** in `config.py`:
   ```python
   CONFIDENCE_THRESHOLD = 0.3  # Lower from 0.5
   ```

2. **Add more training images** of missed cases

3. **Train longer**:
   ```bash
   --epochs 200  # Instead of 100
   ```

### If Model Detects Non-Fish Objects:
1. **Raise confidence threshold**:
   ```python
   CONFIDENCE_THRESHOLD = 0.6  # Higher from 0.5
   ```

2. **Add negative examples** (images without fish)

3. **Add more varied training images**

### If Model is Slow:
- Already optimized with `YOLO_IMG_SIZE = 320`
- Consider using YOLOv8n (nano) not larger models
- Follow FPS optimization guide

---

## Quick Training Methods

### Method 1: Use Existing Fish Datasets

Download pre-labeled fish datasets:

**Roboflow Universe:**
```bash
# Search for fish datasets
# Example: "Fish Detection Dataset" on Roboflow
# Download in YOLOv8 format
```

**Kaggle Datasets:**
- Fish Species Recognition Dataset
- Underwater Fish Detection
- Aquarium Fish Detection

### Method 2: Transfer Learning (Fastest)

Use a model already trained on fish:

```python
# Instead of yolov8n.pt, use a fish-pretrained model
# Search "yolov8 fish detection" on GitHub
```

---

## Training Time Estimates

| Device | Training Time (100 epochs) |
|--------|---------------------------|
| Raspberry Pi 4 | 4-8 hours |
| Laptop (no GPU) | 2-4 hours |
| Laptop (with GPU) | 20-40 minutes |
| Google Colab (free GPU) | 15-30 minutes |
| Roboflow Cloud | 10-20 minutes |

**Recommendation**: Train on Google Colab (free GPU) then copy model to Pi!

---

## Sample Data Collection Script

I've included a data collection script:

```bash
# Collect 500 fish images automatically
python3 -c "
from camera_handler import CameraHandler
from config import Config
import cv2
import time
import os

os.makedirs('dataset/images/raw', exist_ok=True)

config = Config()
camera = CameraHandler(config)
camera.start()

print('Auto-capturing 500 images (1 per second)...')

for i in range(500):
    frame = camera.capture_frame()
    if frame is not None:
        filename = f'dataset/images/raw/capture_{i:04d}.jpg'
        cv2.imwrite(filename, frame)
        print(f'Captured {i+1}/500: {filename}')
    time.sleep(1)

camera.stop()
print('Done! Now annotate images using LabelImg or Roboflow.')
"
```

---

## Recommended Workflow

### For Best Results:

1. **Collect 300-500 images** from your actual pond
   - Various times of day
   - Different weather conditions
   - Include both healthy and sick fish

2. **Annotate using Roboflow** (easiest)
   - Upload to roboflow.com
   - Draw boxes around fish
   - Export as YOLOv8 format

3. **Train on Google Colab** (fastest)
   - Free GPU available
   - 15-30 minutes training time
   - Download trained model

4. **Copy model to Pi**
   ```bash
   scp best.pt pi@raspberrypi.local:~/Documents/GitHub/ishara-iot/models/fish_detection.pt
   ```

5. **Test and adjust**
   ```bash
   ./start.sh
   # Watch for false positives/negatives
   # Adjust CONFIDENCE_THRESHOLD if needed
   ```

---

## Troubleshooting

### "Out of Memory" During Training
```python
# Reduce batch size
--batch 4  # or even 2

# Or reduce image size
--imgsz 256
```

### "No fish detected" with Trained Model
```python
# Lower confidence threshold
CONFIDENCE_THRESHOLD = 0.3

# Check if model file exists
ls -lh models/fish_detection.pt
```

### "Still detecting non-fish objects"
- Add more negative examples to training data
- Increase confidence threshold
- Retrain with more varied fish images

---

## Next Steps

1. **Collect images**: Use the camera capture script
2. **Annotate**: Use Roboflow (easiest) or LabelImg
3. **Train**: Use Google Colab (fastest) or Pi 4 (slow)
4. **Deploy**: Copy model to `models/fish_detection.pt`
5. **Test**: Run `./start.sh` and monitor results

The trained model will **dramatically improve accuracy** by learning your specific fish species and environment! 🐟✅

---

## Additional Resources

- **YOLOv8 Docs**: https://docs.ultralytics.com
- **Roboflow**: https://roboflow.com (annotation + training)
- **LabelImg**: https://github.com/heartexlabs/labelImg
- **Google Colab**: https://colab.research.google.com
- **Fish Datasets**: Search "fish detection dataset" on Kaggle/Roboflow
