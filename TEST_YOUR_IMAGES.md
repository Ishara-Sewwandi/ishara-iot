# Quick Start: Test Your Own Fish Images

This guide shows you how to quickly test the fish health detection system with your own images.

## 📁 Folder Structure

```
test_images/
├── input/          ← Place your images here
├── output/         ← Results appear here
└── README.md       ← Detailed instructions
```

## 🚀 Quick Start (3 Steps)

### Step 1: Upload Your Images

Copy your fish images to the `test_images/input/` folder:

```bash
# Example: Copy a single image
cp ~/Pictures/my_fish.jpg test_images/input/

# Example: Copy multiple images
cp ~/Pictures/*.jpg test_images/input/
```

**Supported formats:** JPG, JPEG, PNG, BMP

### Step 2: Run the Test

```bash
# Method 1: Python script
python3 test_my_images.py

# Method 2: Shell script
./test_my_images.sh
```

### Step 3: View Results

Check the `test_images/output/` folder for:
- **Annotated images** with detection boxes and health status
- **Results report** with detailed analysis

```bash
# View output folder
ls -lh test_images/output/

# View latest results
cat test_images/output/results_*.txt
```

## 📊 What You'll Get

### Annotated Images
- Fish detection bounding boxes
- Health status labels (healthy, bacterial, fungal, parasitic, dead, white_tail)
- Confidence scores
- Color-coded boxes (green=healthy, orange/purple/blue=diseases, red=dead)

### Results Report
- Number of fish detected per image
- Health classification for each fish
- Confidence scores
- Processing timestamp

## 💡 Examples

### Example 1: Test Single Image

```bash
# Copy your image
cp my_fish_photo.jpg test_images/input/

# Run test
python3 test_my_images.py

# View result
eog test_images/output/result_my_fish_photo_*.jpg
```

### Example 2: Test Multiple Images

```bash
# Copy all your fish images
cp ~/fish_photos/*.jpg test_images/input/

# Run test (processes all images)
python3 test_my_images.py

# Results for all images will be in output folder
```

### Example 3: Batch Testing

```bash
# Test different batches
mkdir test_images/input/batch1
mkdir test_images/input/batch2

# Move images and test each batch
mv test_images/input/*.jpg test_images/input/batch1/
python3 test_my_images.py

# Clean and test next batch
rm -rf test_images/input/batch1
mv test_images/input/batch2/*.jpg test_images/input/
python3 test_my_images.py
```

## 🎨 Color Coding

The system uses color-coded bounding boxes:

| Health Status | Color  | Severity |
|---------------|--------|----------|
| Healthy       | 🟢 Green | Normal |
| Bacterial     | 🟠 Orange | High |
| Fungal        | 🟣 Purple | High |
| Parasitic     | 🔵 Blue | High |
| White Tail    | 🔵 Blue | High |
| Dead          | 🔴 Red | Critical |

## 🔧 Troubleshooting

### No images found
```
Error: NO IMAGES FOUND!
```
**Solution:** Make sure you copied images to `test_images/input/` folder

### Model not found
```
Error: Fish detection model not found!
```
**Solution:** Train or download the fish detection model first:
```bash
python3 train_model.py
```

### No fish detected
```
Info: No fish detected in this image
```
**Possible reasons:**
- Image quality is too low
- Fish are too small or not clearly visible
- Image is too dark or blurry

**Tips for better results:**
- Use well-lit images
- Ensure fish are clearly visible
- Avoid heavily cluttered backgrounds
- Use images with resolution > 640x480

## 📸 Tips for Best Results

1. **Image Quality:** Use clear, well-lit images
2. **Resolution:** Higher resolution = better detection (recommended: 1080p+)
3. **Fish Size:** Fish should occupy at least 10% of image
4. **Lighting:** Good lighting helps health classification
5. **Background:** Clear water background works best

## 🔄 Cleanup

To clean up and start fresh:

```bash
# Remove all input images
rm test_images/input/*.jpg
rm test_images/input/*.png

# Remove all output results
rm test_images/output/*

# Or clean both at once
rm -rf test_images/input/* test_images/output/*
```

## 📝 Notes

- The script processes all images in the input folder
- Results include timestamps to track different test runs
- Original images are not modified (copies are saved with annotations)
- You can test as many images as you want at once
- Processing time depends on image size and number of fish detected

## 🆘 Need Help?

If you encounter issues:

1. Check that models are trained and available in `models/` folder
2. Verify image format is supported (JPG, PNG, BMP)
3. Ensure images are readable (try opening with image viewer)
4. Check system logs: `tail -f fish_monitoring.log`

---

**Ready to test?** Upload your images and run `python3 test_my_images.py`! 🐟
