@echo off
REM ============================================================
REM Quick Start - Fish Monitoring System
REM One-click launcher with menu
REM ============================================================

:MENU
cls
echo.
echo ============================================================
echo     FISH MORTALITY DETECTION SYSTEM
echo ============================================================
echo.
echo Please select an option:
echo.
echo   1. Start Monitoring System Only
echo   2. Start API Server Only
echo   3. Start EVERYTHING (Monitoring + API)
echo   4. Test Fish Detection
echo   5. Train Fish Detection Model
echo   6. Train Health Classifier
echo   7. View System Information
echo   8. Exit
echo.
echo ============================================================
echo.

set /p choice="Enter your choice (1-8): "

if "%choice%"=="1" goto START_MONITOR
if "%choice%"=="2" goto START_API
if "%choice%"=="3" goto START_ALL
if "%choice%"=="4" goto TEST_DETECTOR
if "%choice%"=="5" goto TRAIN_DETECTION
if "%choice%"=="6" goto TRAIN_HEALTH
if "%choice%"=="7" goto SYSTEM_INFO
if "%choice%"=="8" goto EXIT

echo Invalid choice. Please try again.
timeout /t 2 /nobreak >nul
goto MENU

:START_MONITOR
cls
echo Starting Main Monitoring System...
echo.
python main.py
pause
goto MENU

:START_API
cls
echo Starting API Server on http://localhost:5000...
echo.
python api_server.py
pause
goto MENU

:START_ALL
cls
echo Starting ALL Components...
echo.
call start_all.bat
goto MENU

:TEST_DETECTOR
cls
echo Testing Fish Detector...
echo.
python test_detector.py
pause
goto MENU

:TRAIN_DETECTION
cls
echo Training Fish Detection Model...
echo This will take several hours. Continue? (Y/N)
set /p confirm=
if /i "%confirm%"=="Y" (
    python train_model.py --data dataset/fish_detection/images/data.yaml --epochs 50 --batch-size 8 --img-size 416
)
pause
goto MENU

:TRAIN_HEALTH
cls
echo Training Fish Health Classifier...
echo This will take time. Continue? (Y/N)
set /p confirm=
if /i "%confirm%"=="Y" (
    python train_fish_health_classifier.py --data dataset/fish_health --epochs 50 --imgsz 224 --batch 16
)
pause
goto MENU

:SYSTEM_INFO
cls
echo ============================================================
echo SYSTEM INFORMATION
echo ============================================================
echo.
echo Python Version:
python --version
echo.
echo Installed Models:
dir /b models\*.pt 2>nul || echo No models found
echo.
echo Dataset Statistics:
echo.
echo Fish Detection Dataset:
dir /s /b "dataset\fish_detection\images\train\images\*.jpg" 2>nul | find /c ".jpg" || echo 0
echo   Training images
echo.
echo Fish Health Dataset:
dir /s /b "dataset\fish_health\train\*\*.jpg" 2>nul | find /c ".jpg" || echo 0
echo   Training images
echo.
echo Key Dependencies:
python -c "import cv2; print('OpenCV:', cv2.__version__)" 2>nul || echo OpenCV: Not installed
python -c "import ultralytics; print('YOLOv8:', ultralytics.__version__)" 2>nul || echo YOLOv8: Not installed
echo.
pause
goto MENU

:EXIT
echo.
echo Thank you for using Fish Mortality Detection System!
echo.
exit /b 0
