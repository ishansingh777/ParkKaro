@echo off
title ParkKaro - Smart Parking Intelligence
echo ===================================================
echo   Starting ParkKaro Live Parking Platform
echo   Connecting to Supabase PostGIS...
echo   Backend + Live Map UI on http://localhost:8000
echo ===================================================
timeout /t 2 /nobreak >nul
start http://localhost:8000/home
cd backend
if exist "..\services\api\venv\Scripts\uvicorn.exe" (
    ..\services\api\venv\Scripts\uvicorn.exe main:app --reload --host 0.0.0.0 --port 8000
) else (
    python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
)
pause
