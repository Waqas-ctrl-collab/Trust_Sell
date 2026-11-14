@echo off
cd /d "%~dp0frontend"
if not exist node_modules (
  echo Installing dependencies...
  call npm install
  if errorlevel 1 exit /b 1
)
echo Starting TrustSell at http://127.0.0.1:5173/
call npm run dev
pause
