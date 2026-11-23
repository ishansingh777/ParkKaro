# Start ParkKaro FastAPI Backend & Web UI
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "  Starting ParkKaro FastAPI Backend & Web UI" -ForegroundColor Green
Write-Host "  Connecting to Supabase PostGIS..." -ForegroundColor Yellow
Write-Host "  Interactive UI: http://localhost:8000" -ForegroundColor White
Write-Host "  Swagger Docs:   http://localhost:8000/docs" -ForegroundColor White
Write-Host "==============================================" -ForegroundColor Cyan

Set-Location -Path "$PSScriptRoot\services\api"
& ".\venv\Scripts\uvicorn.exe" app.main:app --reload --host 0.0.0.0 --port 8000
