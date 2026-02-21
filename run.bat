@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo    AI Pollution Monitor - Starting up
echo ==========================================

:: Check if port 8000 is already in use
netstat -ano | findstr :8000 | findstr LISTENING > nul
if %ERRORLEVEL% equ 0 (
    echo [WARNING] Port 8000 appears to be in use. 
    echo If the dashboard doesn't load, close other terminal windows first.
    echo.
)

:: Initialize DB
echo [1/2] Initializing database...
python app/db/init_db.py

:: Run the FastAPI server
echo [2/2] Launching server...
echo.
echo Dashboard will be available at: http://localhost:8000
echo.
python -m uvicorn app.main:app --reload --port 8000

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] The server failed to start.
    echo Please make sure Python is installed and port 8000 is free.
    pause
)
