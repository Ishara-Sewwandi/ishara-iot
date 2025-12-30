# Test Images Folder

## How to Use This Folder

### 1. Upload Your Images
Place your fish images in the `input` folder to test the detection system.

### 2. Run Tests
Use the test script to analyze your images:
```bash
python test_my_images.py
```

### 3. View Results
Check the `output` folder for:
- Annotated images with detection boxes
- Health classification results
- Analysis reports

## Folder Structure
```
test_images/
├── input/          # Place your test images here
├── output/         # Processed results appear here
└── README.md       # This file
```

## Supported Image Formats
- JPG/JPEG
- PNG
- BMP

## Tips
- Use clear, well-lit images for best results
- Images can contain single or multiple fish
- Results include health status and confidence scores
