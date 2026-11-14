# TrustSell Installer

## Files in this folder

| File | Purpose |
|------|---------|
| `TrustSell.iss` | Main Inno Setup 6 script — compile this to build the `.exe` |
| `check_install.bat` | Runs on target PC to install Python, Node.js, venv, and packages |
| `launch.bat` | Starts both backend and frontend servers |
| `TrustSell_launcher.bat` | Shortcut wrapper for launch.bat |
| `output/` | Created automatically — contains the final `.exe` |

## How to build the installer

1. Open **Inno Setup 6** (already installed)
2. Click **File → Open** and select `TrustSell.iss`
3. Click **Build → Compile** (or press `F9`)
4. The installer `.exe` will appear in `installer\output\TrustSell_Setup_v1.0.0.exe`

## What the installer does on the target PC

1. Copies all app files to `C:\TrustSell\`
2. Checks if Python 3.12 is installed → installs it if not
3. Checks if Node.js 22 is installed → installs it if not
4. Creates a Python virtual environment at `C:\TrustSell\backend\venv`
5. Runs `pip install -r requirements.txt` inside the venv
6. Runs `npm install` for the frontend
7. Creates Desktop and Start Menu shortcuts

## Requirements to build

- Inno Setup 6 installed
- All source files present at `D:\Trust sell\`

## Notes

- Target PC needs internet access during install (to download Python/Node if missing)
- The install process may take 5-10 minutes on a fresh PC
- MongoDB is not required — the app uses an in-memory mock for local development
