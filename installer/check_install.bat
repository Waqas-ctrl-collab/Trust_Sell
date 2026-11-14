@echo off
:: ============================================================
:: TrustSell - Dependency Checker & Installer
:: Called by Inno Setup during installation
:: ============================================================
setlocal EnableDelayedExpansion

set INSTALL_DIR=%~dp0
:: Remove trailing backslash
if "%INSTALL_DIR:~-1%"=="\" set INSTALL_DIR=%INSTALL_DIR:~0,-1%

echo ============================================================
echo  TrustSell - Setting up dependencies...
echo  Install directory: %INSTALL_DIR%
echo ============================================================
echo.

:: ------------------------------------------------------------
:: STEP 1: Check Python
:: ------------------------------------------------------------
echo [1/6] Checking Python...
set PYTHON_EXE=
for %%i in (python.exe) do set PYTHON_EXE=%%~$PATH:i

if "%PYTHON_EXE%"=="" (
    if exist "C:\Python312\python.exe" set PYTHON_EXE=C:\Python312\python.exe
    if exist "C:\Program Files\Python312\python.exe" set PYTHON_EXE=C:\Program Files\Python312\python.exe
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
    if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python314\python.exe
    if exist "%LOCALAPPDATA%\Programs\Python\Python315\python.exe" set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python315\python.exe
)

if "%PYTHON_EXE%"=="" (
    echo Python not found. Downloading and installing Python 3.12...
    curl -L --progress-bar -o "%TEMP%\python_installer.exe" "https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe"
    if errorlevel 1 (
        echo ERROR: Failed to download Python. Check your internet connection.
        pause
        exit /b 1
    )
    "%TEMP%\python_installer.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_launcher=1
    if errorlevel 1 (
        echo ERROR: Python installation failed.
        pause
        exit /b 1
    )
    del "%TEMP%\python_installer.exe"
    set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
    echo Python installed successfully.
) else (
    echo Python found: %PYTHON_EXE% - OK
)

:: ------------------------------------------------------------
:: STEP 2: Check Node.js
:: ------------------------------------------------------------
echo.
echo [2/6] Checking Node.js...
set NODE_EXE=
for %%i in (node.exe) do set NODE_EXE=%%~$PATH:i

if "%NODE_EXE%"=="" (
    if exist "C:\Program Files\nodejs\node.exe" set NODE_EXE=C:\Program Files\nodejs\node.exe
)

if "%NODE_EXE%"=="" (
    echo Node.js not found. Downloading and installing Node.js LTS...
    curl -L --progress-bar -o "%TEMP%\node_installer.msi" "https://nodejs.org/dist/v22.16.0/node-v22.16.0-x64.msi"
    if errorlevel 1 (
        echo ERROR: Failed to download Node.js. Check your internet connection.
        pause
        exit /b 1
    )
    msiexec /i "%TEMP%\node_installer.msi" /quiet /norestart ADDLOCAL=ALL
    if errorlevel 1 (
        echo ERROR: Node.js installation failed.
        pause
        exit /b 1
    )
    del "%TEMP%\node_installer.msi"
    set PATH=%PATH%;C:\Program Files\nodejs
    echo Node.js installed successfully.
) else (
    echo Node.js found: %NODE_EXE% - OK
)

set PATH=%PATH%;C:\Program Files\nodejs

:: ------------------------------------------------------------
:: STEP 3: Check MongoDB
:: ------------------------------------------------------------
echo.
echo [3/6] Checking MongoDB...
set MONGO_INSTALLED=0

:: Check if mongod service exists
sc query MongoDB >nul 2>&1
if %errorlevel% equ 0 set MONGO_INSTALLED=1

:: Check common install paths
if exist "C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe" set MONGO_INSTALLED=1
if exist "C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe" set MONGO_INSTALLED=1
if exist "C:\Program Files\MongoDB\Server\6.0\bin\mongod.exe" set MONGO_INSTALLED=1

if "%MONGO_INSTALLED%"=="0" (
    echo MongoDB not found. Downloading and installing MongoDB 8.0 Community...
    curl -L --progress-bar -o "%TEMP%\mongodb_installer.msi" "https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-8.0.4-signed.msi"
    if errorlevel 1 (
        echo ERROR: Failed to download MongoDB. Check your internet connection.
        pause
        exit /b 1
    )
    echo Installing MongoDB - this may take a few minutes...
    msiexec /i "%TEMP%\mongodb_installer.msi" /quiet /norestart INSTALLLOCATION="C:\Program Files\MongoDB" ADDLOCAL="ServerService,Client,Router,MonitoringTools,ImportExportTools,MiscellaneousTools"
    if errorlevel 1 (
        echo ERROR: MongoDB installation failed.
        pause
        exit /b 1
    )
    del "%TEMP%\mongodb_installer.msi"
    echo MongoDB installed successfully.
    :: Start MongoDB service
    echo Starting MongoDB service...
    net start MongoDB >nul 2>&1
    echo MongoDB service started - OK
) else (
    echo MongoDB found - OK
    :: Make sure service is running
    sc query MongoDB | find "RUNNING" >nul 2>&1
    if errorlevel 1 (
        echo Starting MongoDB service...
        net start MongoDB >nul 2>&1
    )
    echo MongoDB service is running - OK
)

:: ------------------------------------------------------------
:: STEP 4: Create Python virtual environment
:: ------------------------------------------------------------
echo.
echo [4/6] Creating Python virtual environment...
if exist "%INSTALL_DIR%\backend\venv" (
    echo Removing old venv...
    rmdir /s /q "%INSTALL_DIR%\backend\venv"
)

"%PYTHON_EXE%" -m venv "%INSTALL_DIR%\backend\venv"
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment.
    pause
    exit /b 1
)
echo Virtual environment created - OK

:: ------------------------------------------------------------
:: STEP 5: Install Python dependencies
:: ------------------------------------------------------------
echo.
echo [5/6] Installing Python dependencies...
"%INSTALL_DIR%\backend\venv\Scripts\python.exe" -m pip install --upgrade pip
"%INSTALL_DIR%\backend\venv\Scripts\pip.exe" install -r "%INSTALL_DIR%\backend\requirements.txt"
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies.
    pause
    exit /b 1
)
echo Python dependencies installed - OK

:: ------------------------------------------------------------
:: STEP 6: Install Node.js dependencies
:: ------------------------------------------------------------
echo.
echo [6/6] Installing frontend Node.js dependencies...
cd /d "%INSTALL_DIR%\frontend"

set NODE_DIR=
if exist "C:\Program Files\nodejs\node.exe" set NODE_DIR=C:\Program Files\nodejs
if exist "C:\Program Files (x86)\nodejs\node.exe" set NODE_DIR=C:\Program Files (x86)\nodejs

if "%NODE_DIR%"=="" (
    for %%i in (node.exe) do set NODE_DIR=%%~dp$PATH:i
    if not "%NODE_DIR%"=="" set NODE_DIR=%NODE_DIR:~0,-1%
)

if "%NODE_DIR%"=="" (
    echo ERROR: Cannot locate Node.js. Please install Node.js manually and re-run.
    pause
    exit /b 1
)

echo Using Node.js from: %NODE_DIR%
"%NODE_DIR%\node.exe" "%NODE_DIR%\node_modules\npm\bin\npm-cli.js" install
if errorlevel 1 (
    echo ERROR: Failed to install Node.js dependencies.
    pause
    exit /b 1
)
echo Node.js dependencies installed - OK

echo.
echo ============================================================
echo  All dependencies installed successfully!
echo  You can close this window.
echo ============================================================
pause
endlocal
exit /b 0
