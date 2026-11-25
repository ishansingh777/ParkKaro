# All-in-one launcher for ParkKaro Platform
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Starting ParkKaro Live Parking Intelligence Platform" -ForegroundColor Green
Write-Host "  Connecting to Supabase PostGIS..." -ForegroundColor Yellow
Write-Host "  Opening http://localhost:8000/home in your browser..." -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

Start-Process "http://localhost:8000/home"
$VenvUvicorn = Join-Path $PSScriptRoot "services\api\venv\Scripts\uvicorn.exe"
Set-Location -Path "$PSScriptRoot\backend"
if (Test-Path $VenvUvicorn) {
    & $VenvUvicorn main:app --reload --host 0.0.0.0 --port 8000
} else {
    python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
}
