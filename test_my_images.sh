#!/bin/bash
# Test Your Own Fish Images

echo "=========================================="
echo "   Fish Health Testing - Your Images"
echo "=========================================="
echo ""
echo "Upload your images to: test_images/input/"
echo ""
echo "Press Enter to start testing..."
read

# Run the test script
python3 test_my_images.py

echo ""
echo "Check test_images/output/ for results!"
