@echo off
title TrustSell Launcher
cd /d "%~dp0"

echo Starting TrustSell Backend...
start "TrustSell Backend" cmd /k "cd /d "%~dp0backend" && call venv\Scripts\activate.bat && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo Starting TrustSell Frontend...
start "TrustSell Frontend" cmd /k "cd /d "%~dp0frontend" && call refreshenv 2>nul & npm run dev"

echo.
echo Backend  : http://localhost:8000
echo Frontend : http://127.0.0.1:5173
echo.
echo Both servers are running in separate windows.
pause
