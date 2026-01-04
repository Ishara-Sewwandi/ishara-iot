@echo off
REM ============================================================
REM Fish Monitoring System - DEMO MODE (No Hardware Required)
REM Runs with test images/video instead of live camera
REM ============================================================

echo.
echo ============================================================
echo Fish Mortality Detection System - DEMO MODE
echo ============================================================
echo.
echo Running without physical hardware (Camera/GPIO)
echo Using test images and simulated environment
echo.

cd /d "%~dp0"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not installed
    pause
    exit /b 1
)

echo Starting DEMO mode...
echo.
echo Options:
echo   1. Test fish detection on images
echo   2. Start API server (no camera needed)
echo   3. Test alerts system
echo   4. View system info
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto TEST_IMAGES
if "%choice%"=="2" goto START_API
if "%choice%"=="3" goto TEST_ALERTS
if "%choice%"=="4" goto SYSTEM_INFO

echo Invalid choice
pause
exit /b 1

:TEST_IMAGES
cls
echo ============================================================
echo Testing Fish Detection on Your Images
echo ============================================================
echo.
echo Place your fish images in: test_images\input\
echo Results will be saved to: test_images\output\
echo.
pause
python test_my_images.py
echo.
echo Check test_images\output\ for results
pause
exit /b 0

:START_API
cls
echo ============================================================
echo Starting API Server (Demo Mode)
echo ============================================================
echo.
echo API will be available at: http://localhost:5000
echo.
echo Available endpoints:
echo   GET  /status       - System status
echo   GET  /video_feed   - Video stream (if camera available)
echo   GET  /alerts       - Recent alerts
echo   POST /test_alert   - Send test alert
echo.
python api_server.py
pause
exit /b 0

:TEST_ALERTS
cls
echo Testing Alert System...
echo.
python test_alerts.py
pause
exit /b 0

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
for /f %%i in ('dir /s /b "dataset\fish_detection\images\train\images\*.jpg" 2^>nul ^| find /c ".jpg"') do echo   Training: %%i images
for /f %%i in ('dir /s /b "dataset\fish_detection\images\val\images\*.jpg" 2^>nul ^| find /c ".jpg"') do echo   Validation: %%i images
echo.
echo Fish Health Dataset:
for /f %%i in ('dir /s /b "dataset\fish_health\train\*\*.jpg" 2^>nul ^| find /c ".jpg"') do echo   Training: %%i images
for /f %%i in ('dir /s /b "dataset\fish_health\val\*\*.jpg" 2^>nul ^| find /c ".jpg"') do echo   Validation: %%i images
echo.
echo Key Dependencies:
python -c "import cv2; print('OpenCV:', cv2.__version__)" 2>nul || echo OpenCV: Not installed
python -c "import torch; print('PyTorch:', torch.__version__)" 2>nul || echo PyTorch: Not installed
python -c "import ultralytics; print('YOLOv8:', ultralytics.__version__)" 2>nul || echo YOLOv8: Not installed
python -c "import flask; print('Flask:', flask.__version__)" 2>nul || echo Flask: Not installed
echo.
pause
exit /b 0
