# All-in-one launcher for ParkKaro Platform
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Starting ParkKaro Live Parking Intelligence Platform" -ForegroundColor Green
Write-Host "  Connecting to Supabase PostGIS..." -ForegroundColor Yellow
Write-Host "  Opening http://localhost:8000 in your browser..." -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

Start-Process "http://localhost:8000"
Set-Location -Path "$PSScriptRoot\services\api"
& ".\venv\Scripts\uvicorn.exe" app.main:app --reload --host 0.0.0.0 --port 8000
