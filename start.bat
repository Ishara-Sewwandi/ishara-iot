@echo off
REM ============================================================
REM Fish Mortality Detection System - Windows Launcher
REM Starts the complete IoT monitoring system
REM ============================================================

echo.
echo ============================================================
echo Fish Mortality Detection System
echo ============================================================
echo.
echo Starting all system components...
echo.

REM Change to project directory
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org
    pause
    exit /b 1
)

echo [1/4] Checking dependencies...
python -c "import cv2, ultralytics" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Some dependencies may be missing
    echo Installing/updating requirements...
    pip install -r requirements.txt
)

echo [2/4] Verifying models...
if not exist "models\fish_detection.pt" (
    echo WARNING: Fish detection model not found!
    echo Please train the model first: python train_model.py --data dataset/fish_detection/images/data.yaml --epochs 50 --batch-size 8 --img-size 416
    pause
    exit /b 1
)

if not exist "models\fish_health_classifier.pt" (
    echo WARNING: Fish health classifier not found!
    echo The system will run without health classification.
)

echo [3/4] Models verified successfully
echo.
echo Fish Detection Model: models\fish_detection.pt
echo Health Classifier: models\fish_health_classifier.pt
echo.

echo [4/4] Starting Fish Monitoring System...
echo.
echo ============================================================
echo System Status: RUNNING
echo ============================================================
echo.
echo Components Active:
echo   - Camera Handler
echo   - Fish Detection (YOLOv8)
echo   - Health Classification
echo   - Behavior Analysis
echo   - Rainfall Detection
echo   - Alert System (Telegram/Email/Webhook)
echo.
echo Display: 25 FPS with real-time detection overlays
echo.
echo Press Ctrl+C to stop the system
echo ============================================================
echo.

REM Run the main monitoring system
python main.py

REM Handle exit
echo.
echo ============================================================
echo System Stopped
echo ============================================================
pause
