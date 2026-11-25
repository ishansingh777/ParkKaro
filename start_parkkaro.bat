@echo off
title ParkKaro - Smart Parking Intelligence
echo ===================================================
echo   Starting ParkKaro Live Parking Platform
echo   Connecting to Supabase PostGIS & AI Models...
echo   Backend + Live Map UI on http://localhost:8000
echo ===================================================

cd backend

:: Open browser after 4 seconds to ensure uvicorn port is listening
start /b cmd /c "timeout /t 4 /nobreak >nul && start http://localhost:8000/home"

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
