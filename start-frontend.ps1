# Trust Sell — start frontend only
$ErrorActionPreference = "Stop"
$frontend = Join-Path $PSScriptRoot "frontend"

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Node.js/npm is not installed. Install from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path (Join-Path $frontend "node_modules"))) {
    Write-Host "Installing frontend dependencies..."
    Set-Location $frontend
    npm install
} else {
    Set-Location $frontend
}

foreach ($port in 5173, 5174, 5175) {
    Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue |
        ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
}

Write-Host "Starting TrustSell frontend at http://127.0.0.1:5173/" -ForegroundColor Green
npm run dev
