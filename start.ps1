# Trust Sell — start backend + frontend (requires MongoDB on localhost:27017)
$root = $PSScriptRoot

Write-Host "Starting Trust Sell backend on http://127.0.0.1:8000 ..."
Start-Process -FilePath "py" -ArgumentList "-m", "uvicorn", "app.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000" -WorkingDirectory "$root\backend"

Write-Host "Starting Trust Sell frontend on http://localhost:5173 ..."
Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WorkingDirectory "$root\frontend"

Write-Host ""
Write-Host "Open http://localhost:5173 in your browser."
Write-Host "API docs: http://127.0.0.1:8000/docs"
Write-Host "MongoDB must be running (see docker-compose.yml or install MongoDB.Server)."
