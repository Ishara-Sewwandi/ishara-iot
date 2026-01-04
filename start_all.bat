@echo off
REM ============================================================
REM Fish Monitoring System - Complete Launcher
REM Starts BOTH the monitoring system AND API server
REM ============================================================

echo.
echo ============================================================
echo Fish Mortality Detection System - Full Stack
echo ============================================================
echo.
echo Starting ALL system components:
echo   1. Main Monitoring System (Fish Detection + Alerts)
echo   2. REST API Server (Web/Mobile Interface)
echo.

cd /d "%~dp0"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not installed
    pause
    exit /b 1
)

REM Verify models
if not exist "models\fish_detection.pt" (
    echo ERROR: Fish detection model not found!
    echo Please train the model first.
    pause
    exit /b 1
)

echo Starting components...
echo.

REM Start API Server in a new window
echo [1/2] Launching API Server (Port 5000)...
start "Fish Monitoring API Server" cmd /k "python api_server.py"
timeout /t 2 /nobreak >nul

REM Start Main Monitoring System
echo [2/2] Launching Main Monitoring System...
echo.
echo ============================================================
echo All Systems Active!
echo ============================================================
echo.
echo   API Server: http://localhost:5000
echo   Monitoring: Active with 25 FPS display
echo.
echo Press Ctrl+C to stop the monitoring system
echo Close other windows manually to stop API server
echo ============================================================
echo.

python main.py

echo.
echo Main monitoring stopped. Close API server window manually.
pause
