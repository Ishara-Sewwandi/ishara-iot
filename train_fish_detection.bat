@echo off
REM Train Fish Detection Model from Scratch
REM Dataset: Fish or Not Fish (Object Detection)

echo.
echo ============================================================
echo Fish Detection Model Training (YOLOv8)
echo ============================================================
echo.
echo Dataset: D:\ishara-iot\dataset\fish_detection
echo Task: Detect fish in images (Object Detection)
echo.
echo Training Images: 4,067
echo Validation Images: 872
echo Classes: 1 (Koi fish)
echo.
echo Training Settings:
echo   - Model: YOLOv8n (nano - fast)
echo   - Epochs: 100
echo   - Batch: 8
echo   - Image Size: 416x416
echo   - Task: Object Detection (bounding boxes)
echo.
echo Expected time: 4-6 hours
echo ============================================================
echo.

python train_model.py --data dataset/fish_detection/data.yaml --epochs 100 --batch-size 8 --img-size 416

echo.
echo ============================================================
echo Training Complete!
echo ============================================================
echo.

if exist "models\fish_detection.pt" (
    echo Model saved to: models\fish_detection.pt
    echo.
    echo Next steps:
    echo   1. Test detection: python test_my_images.py
    echo   2. Run system: start_all.bat
) else (
    echo WARNING: Model file not found!
    echo Check training output above for errors.
)

echo.
pause
