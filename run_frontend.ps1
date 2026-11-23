# Start ParkKaro Frontend
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "  Starting ParkKaro Frontend UI" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Cyan

Set-Location -Path "$PSScriptRoot\apps\web"

if (Get-Command npm -ErrorAction SilentlyContinue) {
    npm run dev
} else {
    Write-Host "Node.js not detected on system PATH." -ForegroundColor Yellow
    Write-Host "Launching ParkKaro Web UI via Python server on http://localhost:3000..." -ForegroundColor Green
    Set-Location -Path "$PSScriptRoot\apps\web\public"
    Start-Process "http://localhost:3000"
    & "$PSScriptRoot\services\api\venv\Scripts\python.exe" -m http.server 3000
}
