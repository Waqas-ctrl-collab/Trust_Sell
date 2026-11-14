; ============================================================
; TrustSell - Inno Setup 6 Script
; ============================================================

#define AppName "TrustSell"
#define AppVersion "1.0.0"
#define AppPublisher "TrustSell"
#define AppURL "http://localhost:5173"
#define AppExeName "TrustSell.exe"
#define SourceDir "D:\Trust sell"

[Setup]
; Basic app info
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}

; Install directory
DefaultDirName=C:\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=no

; Output
OutputDir={#SourceDir}\installer\output
OutputBaseFilename=TrustSell_Setup_v{#AppVersion}

; Compression
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes

; Appearance
WizardStyle=modern
WizardResizable=yes

; Privileges
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Minimum Windows version (Windows 10)
MinVersion=10.0

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &Desktop shortcut"; GroupDescription: "Additional icons:"
Name: "startmenuicon"; Description: "Create a &Start Menu shortcut"; GroupDescription: "Additional icons:"

[Files]
; Backend files
Source: "{#SourceDir}\backend\app\*"; DestDir: "{app}\backend\app"; Flags: recursesubdirs createallsubdirs; Excludes: "__pycache__,*.pyc"
Source: "{#SourceDir}\backend\requirements.txt"; DestDir: "{app}\backend"
Source: "{#SourceDir}\backend\.env"; DestDir: "{app}\backend"
Source: "{#SourceDir}\backend\uploads\*"; DestDir: "{app}\backend\uploads"; Flags: recursesubdirs createallsubdirs; Excludes: "*.tmp"

; Frontend source files (npm install will run on target machine)
Source: "{#SourceDir}\frontend\src\*"; DestDir: "{app}\frontend\src"; Flags: recursesubdirs createallsubdirs
Source: "{#SourceDir}\frontend\public\*"; DestDir: "{app}\frontend\public"; Flags: recursesubdirs createallsubdirs
Source: "{#SourceDir}\frontend\index.html"; DestDir: "{app}\frontend"
Source: "{#SourceDir}\frontend\package.json"; DestDir: "{app}\frontend"
Source: "{#SourceDir}\frontend\package-lock.json"; DestDir: "{app}\frontend"
Source: "{#SourceDir}\frontend\vite.config.js"; DestDir: "{app}\frontend"
Source: "{#SourceDir}\frontend\eslint.config.js"; DestDir: "{app}\frontend"

; Installer helper scripts
Source: "{#SourceDir}\installer\check_install.bat"; DestDir: "{app}"
Source: "{#SourceDir}\installer\launch.bat"; DestDir: "{app}"

; Launcher VBScript
Source: "{#SourceDir}\installer\launcher.vbs"; DestDir: "{app}"

[Icons]
; Desktop shortcut
Name: "{autodesktop}\{#AppName}"; Filename: "{sys}\wscript.exe"; Parameters: """{app}\launcher.vbs"""; Tasks: desktopicon; Comment: "Launch TrustSell Application"

; Start Menu shortcuts
Name: "{group}\{#AppName}"; Filename: "{sys}\wscript.exe"; Parameters: """{app}\launcher.vbs"""; Comment: "Launch TrustSell Application"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"

[Run]
; Run dependency checker after installation
Filename: "{app}\check_install.bat"; \
    WorkingDir: "{app}"; \
    StatusMsg: "Installing dependencies (Python, Node.js, packages)... This may take several minutes."; \
    Flags: waituntilterminated

; Optionally launch app after install
Filename: "{sys}\wscript.exe"; Parameters: """{app}\launcher.vbs"""; \
    Description: "Launch TrustSell now"; \
    Flags: postinstall nowait skipifsilent unchecked

[UninstallRun]
; Clean up venv and node_modules on uninstall
Filename: "{cmd}"; Parameters: "/c rmdir /s /q ""{app}\backend\venv"""; Flags: runhidden waituntilterminated
Filename: "{cmd}"; Parameters: "/c rmdir /s /q ""{app}\frontend\node_modules"""; Flags: runhidden waituntilterminated

[UninstallDelete]
Type: filesandordirs; Name: "{app}\backend\venv"
Type: filesandordirs; Name: "{app}\frontend\node_modules"
Type: filesandordirs; Name: "{app}\backend\__pycache__"

[Code]
// ============================================================
// Pre-install check: warn user about internet requirement
// ============================================================
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  if MsgBox(
    'TrustSell Setup will:' + #13#10 + #13#10 +
    '  - Install Python 3.12 (if not present)' + #13#10 +
    '  - Install Node.js 22 LTS (if not present)' + #13#10 +
    '  - Install MongoDB 8.0 Community (if not present)' + #13#10 +
    '  - Create a Python virtual environment' + #13#10 +
    '  - Install all backend & frontend dependencies' + #13#10 + #13#10 +
    'An internet connection is required for this step.' + #13#10 +
    'The process may take 5-15 minutes.' + #13#10 + #13#10 +
    'Do you want to continue?',
    mbConfirmation, MB_YESNO) = IDNO then
  begin
    Result := False;
  end;
end;

// ============================================================
// Post-install: show success message with URLs
// ============================================================
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssDone then
  begin
    MsgBox(
      'TrustSell has been installed successfully!' + #13#10 + #13#10 +
      'To start the application, use the Desktop or Start Menu shortcut.' + #13#10 + #13#10 +
      'Once running:' + #13#10 +
      '  Backend  : http://localhost:8000' + #13#10 +
      '  Frontend : http://127.0.0.1:5173' + #13#10 + #13#10 +
      'MongoDB has been installed and will start automatically.',
      mbInformation, MB_OK);
  end;
end;
