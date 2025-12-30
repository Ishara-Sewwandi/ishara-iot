# Fish Health Dataset

## Dataset Structure

The fish health classification dataset should be organized in the following structure:

```
dataset/fish_health/
├── train/
│   ├── healthy/
│   ├── bacterial/
│   ├── fungal/
│   ├── parasitic/
│   ├── dead/
│   └── white_tail/
├── test/
│   ├── healthy/
│   ├── bacterial/
│   ├── fungal/
│   ├── parasitic/
│   ├── dead/
│   └── white_tail/
└── val/
    ├── healthy/
    ├── bacterial/
    ├── fungal/
    ├── parasitic/
    ├── dead/
    └── white_tail/
```

## Dataset Information

### Health Classes

1. **Healthy** - Fish in good health condition
2. **Bacterial** - Fish with bacterial infections
3. **Fungal** - Fish with fungal infections  
4. **Parasitic** - Fish with parasitic infections
5. **Dead** - Dead fish
6. **White Tail** - Fish with white tail disease

### Dataset Splits

- **Training set (train/)**: Images for training the model
- **Validation set (val/)**: Images for validation during training
- **Test set (test/)**: Images for final model evaluation

## Adding Your Own Dataset

### Option 1: Use Existing Dataset (if local)

If you already have the dataset locally, make sure it follows the structure above.

### Option 2: Collect New Images

1. Capture clear images of fish in different health conditions
2. Organize them into the correct folders based on health status
3. Split the images into train/val/test sets (typically 70%/15%/15%)

Example:
```bash
# Place healthy fish images
cp my_healthy_fish_*.jpg dataset/fish_health/train/healthy/

# Place bacterial infection images
cp my_bacterial_*.jpg dataset/fish_health/train/bacterial/

# And so on for other classes...
```

### Option 3: Use Data Augmentation

If you have limited images, use data augmentation in the training script:

```python
python3 train_fish_health_classifier.py
```

The training script includes automatic augmentation like:
- Random rotations
- Flipping
- Color adjustments
- Brightness/contrast variations

## Recommended Dataset Size

For good results:
- **Minimum**: 50 images per class per split
- **Recommended**: 200+ images per class per split
- **Optimal**: 500+ images per class per split

## Image Requirements

- **Format**: JPG, JPEG, or PNG
- **Resolution**: At least 640x640 pixels (higher is better)
- **Quality**: Clear, well-lit images
- **Content**: Fish should be clearly visible
- **Variety**: Different angles, lighting conditions, backgrounds

## Dataset Sources

You can collect images from:

1. **Your Own Fish Tank**: Capture images directly from your aquaculture setup
2. **Public Datasets**: Search for fish disease datasets on:
   - Kaggle
   - Roboflow
   - Google Dataset Search
3. **Research Papers**: Many papers include datasets
4. **Collaborators**: Partner with other fish farmers or researchers

## Training

Once your dataset is ready:

```bash
# Train the model
python3 train_fish_health_classifier.py

# Monitor training progress
./monitor_training.sh
```

## Notes

- The dataset images are not included in the GitHub repository due to size
- You need to provide your own dataset following the structure above
- Make sure you have the rights to use any external datasets
- For best results, use high-quality, labeled images

## Example Dataset Stats

A typical dataset might contain:

| Class      | Train | Val | Test | Total |
|------------|-------|-----|------|-------|
| Healthy    | 700   | 150 | 150  | 1000  |
| Bacterial  | 560   | 120 | 120  | 800   |
| Fungal     | 560   | 120 | 120  | 800   |
| Parasitic  | 350   | 75  | 75   | 500   |
| Dead       | 280   | 60  | 60   | 400   |
| White Tail | 350   | 75  | 75   | 500   |
| **Total**  | 2800  | 600 | 600  | 4000  |

## Need Help?

- Check `TRAINING_GUIDE.md` for training instructions
- See `TEST_YOUR_IMAGES.md` for testing your trained model
- Review `fish_health_detector.py` for implementation details
