# Start ParkKaro FastAPI Backend
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "  Starting ParkKaro FastAPI Backend" -ForegroundColor Green
Write-Host "  Connecting to Supabase PostGIS..." -ForegroundColor Yellow
Write-Host "==============================================" -ForegroundColor Cyan

Set-Location -Path "$PSScriptRoot\services\api"
& ".\venv\Scripts\uvicorn.exe" app.main:app --reload --host 0.0.0.0 --port 8000
