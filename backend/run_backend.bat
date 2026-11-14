@echo off
title TrustSell Backend Server
cd /d "%~dp0"
echo Starting TrustSell FastAPI Backend on http://localhost:8000 ...
"C:\Users\INSPIRE COMP\AppData\Local\Programs\Python\Python314\python.exe" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause
