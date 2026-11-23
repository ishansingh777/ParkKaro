@echo off
echo ==============================================
echo   Starting ParkKaro FastAPI Backend & Web UI
echo   Connecting to Supabase PostGIS...
echo   Open UI at: http://localhost:8000
echo   API Docs at: http://localhost:8000/docs
echo ==============================================
cd services\api
.\venv\Scripts\uvicorn.exe app.main:app --reload --host 0.0.0.0 --port 8000
pause
