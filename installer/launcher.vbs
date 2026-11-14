' ============================================================
' TrustSell - Silent Launcher
' Starts MongoDB, backend and frontend
' ============================================================

Dim objShell
Dim strInstallDir

Set objShell = CreateObject("WScript.Shell")

' Get the directory where this vbs file lives
strInstallDir = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\") - 1)

' ---- Start MongoDB service (if not already running) ----
objShell.Run "cmd /c net start MongoDB", 0, True

' Wait 2 seconds for MongoDB to start
WScript.Sleep 2000

' ---- Start Backend ----
objShell.Run "cmd /k ""cd /d """ & strInstallDir & "\backend"" && """ & strInstallDir & "\backend\venv\Scripts\python.exe"" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000""", 1, False

' Wait 6 seconds for backend to fully initialize
WScript.Sleep 6000

' ---- Start Frontend ----
objShell.Run "cmd /k ""cd /d """ & strInstallDir & "\frontend"" && ""C:\Program Files\nodejs\node.exe"" ""C:\Program Files\nodejs\node_modules\npm\bin\npm-cli.js"" run dev""", 1, False

' Wait 5 seconds for frontend to start
WScript.Sleep 5000

' ---- Open browser ----
objShell.Run "http://127.0.0.1:5173", 1, False

Set objShell = Nothing
