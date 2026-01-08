@echo off
REM Train Fish Health Classifier with Optimized Settings for Balanced Dataset

echo.
echo ============================================================
echo Fish Health Classifier Training
echo ============================================================
echo.
echo Dataset: Balanced (140 images per class)
echo Classes: bacterial, dead, fungal, healthy, parasitic, white_tail
echo.
echo Training Settings:
echo   - Epochs: 100 (full training, no early stopping)
echo   - Batch: 16
echo   - Image Size: 224x224
echo   - Enhanced augmentation
echo.
echo Expected time: 1-2 hours
echo ============================================================
echo.

pause

python train_fish_health_classifier.py --data dataset/fish_health --epochs 100 --batch 16 --imgsz 224

echo.
echo ============================================================
echo Training Complete!
echo ============================================================
echo.
echo Model saved to: models/fish_health_classifier.pt
echo.
echo Next steps:
echo   1. Test with: python test_my_images.py
echo   2. Run system: start_all.bat
echo.
pause
