#!/bin/bash
# Simple menu for testing images

clear
echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Fish Health Detection - Test Your Own Images          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "What would you like to do?"
echo ""
echo "  1) Upload and test images"
echo "  2) View test results"
echo "  3) Clean input folder"
echo "  4) Clean output folder"
echo "  5) View instructions"
echo "  0) Exit"
echo ""
read -p "Select option [0-5]: " choice

case $choice in
    1)
        echo ""
        echo "Step 1: Copy your images to test_images/input/"
        echo "Example: cp your_fish.jpg test_images/input/"
        echo ""
        read -p "Press Enter when images are ready..."
        echo ""
        echo "Running detection..."
        python3 test_my_images.py
        echo ""
        read -p "Press Enter to continue..."
        ;;
    2)
        echo ""
        if [ -d "test_images/output" ]; then
            echo "Files in output folder:"
            ls -lh test_images/output/
            echo ""
            echo "View latest results file?"
            read -p "Press Enter to view or Ctrl+C to cancel..."
            latest=$(ls -t test_images/output/results_*.txt 2>/dev/null | head -1)
            if [ -n "$latest" ]; then
                cat "$latest"
            else
                echo "No results files found."
            fi
        else
            echo "Output folder is empty."
        fi
        echo ""
        read -p "Press Enter to continue..."
        ;;
    3)
        echo ""
        read -p "Remove all images from input folder? (y/N): " confirm
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            rm -f test_images/input/*.jpg
            rm -f test_images/input/*.jpeg
            rm -f test_images/input/*.png
            rm -f test_images/input/*.bmp
            echo "✓ Input folder cleaned"
        else
            echo "Cancelled"
        fi
        echo ""
        read -p "Press Enter to continue..."
        ;;
    4)
        echo ""
        read -p "Remove all results from output folder? (y/N): " confirm
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            rm -rf test_images/output/*
            echo "✓ Output folder cleaned"
        else
            echo "Cancelled"
        fi
        echo ""
        read -p "Press Enter to continue..."
        ;;
    5)
        echo ""
        cat << 'EOF'
╔════════════════════════════════════════════════════════════╗
║                    INSTRUCTIONS                             ║
╚════════════════════════════════════════════════════════════╝

QUICK START:
1. Copy your fish images to: test_images/input/
   Example: cp my_fish.jpg test_images/input/

2. Run this menu and select option 1

3. Check results in: test_images/output/

SUPPORTED FORMATS:
- JPG/JPEG
- PNG  
- BMP

WHAT YOU GET:
- Annotated images with detection boxes
- Health status for each fish
- Confidence scores
- Detailed results report

For more details, see: TEST_YOUR_IMAGES.md
EOF
        echo ""
        read -p "Press Enter to continue..."
        ;;
    0)
        echo ""
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo ""
        echo "Invalid option. Please try again."
        sleep 2
        ;;
esac

# Loop back to menu
exec "$0"
