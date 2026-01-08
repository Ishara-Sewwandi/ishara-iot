@echo off
REM Train Fish Health Classifier - 3 Classes (Dead, Healthy, Unhealthy)

echo.
echo ============================================================
echo Fish Health Classifier Training - 3 Classes
echo ============================================================
echo.
echo Dataset: D:\ishara-iot\dataset\fish_health
echo Classes: dead, healthy, unhealthy
echo Images per class: 840
echo.
echo Training Settings:
echo   - Epochs: 100
echo   - Batch: 16  
echo   - Image Size: 224x224
echo   - Model: YOLOv8n-cls
echo   - No early stopping (trains full 100 epochs)
echo.
echo Expected time: 2-3 hours
echo ============================================================
echo.

python train_fish_health_classifier.py --data dataset/fish_health --epochs 100 --batch 16 --imgsz 224

echo.
echo ============================================================
echo Training Complete!
echo ============================================================
echo.

if exist "models\fish_health_classifier.pt" (
    echo Model saved to: models\fish_health_classifier.pt
    echo.
    echo Next steps:
    echo   1. Test: python test_my_images.py
    echo   2. Run system: start_all.bat
) else (
    echo WARNING: Model file not found!
    echo Check training output above for errors.
)

echo.
pause
