#!/bin/bash
# Quick menu for fish detection training

echo "=========================================="
echo "Fish Detection Model Training - Quick Menu"
echo "=========================================="
echo ""
echo "Current Status:"
echo "  • Model: YOLOv8n (generic - detects any object)"
echo "  • Issue: Detects non-fish objects as fish"
echo "  • Solution: Train custom model on YOUR fish"
echo ""
echo "=========================================="
echo "Options:"
echo "=========================================="
echo ""
echo "1. Capture Fish Images"
echo "   └─ Collect training data from camera"
echo ""
echo "2. Train Custom Model"
echo "   └─ Train YOLOv8 on your fish dataset"
echo ""
echo "3. Test Trained Model"
echo "   └─ Verify model accuracy"
echo ""
echo "4. View Training Guide"
echo "   └─ Complete instructions"
echo ""
echo "5. View Quick Start"
echo "   └─ Fast training workflow"
echo ""
echo "6. Back to Main Menu"
echo ""
echo "=========================================="
read -p "Choose option (1-6): " choice

case $choice in
    1)
        echo ""
        echo "Capture Mode:"
        echo "  1. Manual (press SPACE to capture)"
        echo "  2. Auto (capture N images)"
        echo "  3. Time-lapse (capture over time)"
        read -p "Choose (1-3): " mode
        
        case $mode in
            1)
                python3 capture_fish_images.py --mode manual
                ;;
            2)
                read -p "Number of images: " num
                read -p "Interval (seconds): " interval
                python3 capture_fish_images.py --mode auto --num $num --interval $interval
                ;;
            3)
                read -p "Duration (minutes): " duration
                read -p "Interval (seconds): " interval
                python3 capture_fish_images.py --mode timelapse --duration $duration --interval $interval
                ;;
        esac
        ;;
    
    2)
        echo ""
        echo "Training requires:"
        echo "  • Annotated dataset (use Roboflow or LabelImg)"
        echo "  • dataset/fish_dataset.yaml configured"
        echo "  • 2-6 hours on Pi 4 (or 15min on GPU)"
        echo ""
        read -p "Continue? (y/n): " confirm
        
        if [ "$confirm" = "y" ]; then
            read -p "Dataset YAML [dataset/fish_dataset.yaml]: " data
            data=${data:-dataset/fish_dataset.yaml}
            
            read -p "Epochs [100]: " epochs
            epochs=${epochs:-100}
            
            read -p "Batch size [8]: " batch
            batch=${batch:-8}
            
            python3 train_model.py --data $data --epochs $epochs --batch $batch --imgsz 320
        fi
        ;;
    
    3)
        python3 test_detector.py
        ;;
    
    4)
        less TRAINING_GUIDE.md
        ;;
    
    5)
        less TRAINING_QUICKSTART.md
        ;;
    
    6)
        ./menu.sh
        ;;
    
    *)
        echo "Invalid option"
        ;;
esac
