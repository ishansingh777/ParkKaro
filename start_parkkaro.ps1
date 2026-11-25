# All-in-one launcher for ParkKaro Platform
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Starting ParkKaro Live Parking Intelligence Platform" -ForegroundColor Green
Write-Host "  Connecting to Supabase PostGIS & AI Models..." -ForegroundColor Yellow
Write-Host "  Backend + Live Map UI on http://localhost:8000" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

Set-Location -Path "$PSScriptRoot\backend"

# Launch browser with 4s delay in background so uvicorn is ready
Start-Job -ScriptBlock { Start-Sleep -Seconds 4; Start-Process "http://localhost:8000/home" } | Out-Null

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
