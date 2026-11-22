# Start ParkKaro Next.js Frontend
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "  Starting ParkKaro Next.js Frontend" -ForegroundColor Green
Write-Host "  Opening http://localhost:3000" -ForegroundColor Yellow
Write-Host "==============================================" -ForegroundColor Cyan

Set-Location -Path "$PSScriptRoot\apps\web"
npm run dev
