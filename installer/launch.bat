@echo off
:: ============================================================
:: TrustSell - Launch Script
:: ============================================================
title TrustSell Launcher
cd /d "%~dp0"

:: Check venv exists
if not exist "%~dp0backend\venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found.
    echo Please run check_install.bat first.
    pause
    exit /b 1
)

:: Check node_modules exists
if not exist "%~dp0frontend\node_modules" (
    echo ERROR: Frontend dependencies not found.
    echo Please run check_install.bat first.
    pause
    exit /b 1
)

echo ============================================================
echo  Starting TrustSell...
echo ============================================================
echo.

:: Start Backend using venv python directly (no activation needed)
echo Starting Backend server...
start "TrustSell Backend" cmd /k "cd /d "%~dp0backend" && "%~dp0backend\venv\Scripts\python.exe" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

:: Wait 3 seconds for backend to initialize
timeout /t 3 /nobreak >nul

:: Start Frontend
echo Starting Frontend server...
start "TrustSell Frontend" cmd /k "cd /d "%~dp0frontend" && "C:\Program Files\nodejs\node.exe" "C:\Program Files\nodejs\node_modules\npm\bin\npm-cli.js" run dev"

echo.
echo Backend  : http://localhost:8000
echo Frontend : http://127.0.0.1:5173
echo.
echo Both servers are running in separate windows.
timeout /t 5 /nobreak >nul
