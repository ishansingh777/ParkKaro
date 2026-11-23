@echo off
echo ==============================================
echo   Starting ParkKaro Frontend UI
echo ==============================================
where npm >nul 2>nul
if %errorlevel% equ 0 (
    cd apps\web
    npm run dev
) else (
    echo Node.js not detected on system PATH.
    echo Launching ParkKaro Web UI on http://localhost:3000...
    timeout /t 2 /nobreak >nul
    start http://localhost:3000
    cd apps\web\public
    ..\..\services\api\venv\Scripts\python.exe -m http.server 3000
)
pause
