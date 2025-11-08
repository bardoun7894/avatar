@echo off
REM Call Center System Start Script for Windows

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   Call Center System Startup
echo ========================================
echo.

REM Check Python
where python >nul 2>nul
if errorlevel 1 (
    echo Error: Python is not installed
    pause
    exit /b 1
)

REM Check Node.js
where node >nul 2>nul
if errorlevel 1 (
    echo Error: Node.js is not installed
    pause
    exit /b 1
)

REM Setup backend
echo Setting up backend API...
cd callCenter

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -q -r requirements.txt

REM Setup frontend
echo Setting up frontend...
cd ..\frontend

if not exist "node_modules" (
    echo Installing Node.js dependencies...
    call npm install -q
)

REM Create environment file if it doesn't exist
if not exist ".env.local" (
    echo Creating .env.local...
    (
        echo NEXT_PUBLIC_API_URL=http://localhost:8000
    ) > .env.local
)

REM Start services
echo.
echo ========================================
echo   Starting Services
echo ========================================
echo.

echo Starting backend API on port 8000...
cd ..\callCenter
call venv\Scripts\activate.bat
start /B pythonw main.py
timeout /t 2 /nobreak

echo Starting frontend on port 3000...
cd ..\frontend
start /B npm run dev

timeout /t 3 /nobreak

echo.
echo ========================================
echo   Services Started Successfully!
echo ========================================
echo.
echo Frontend:    http://localhost:3000
echo API:         http://localhost:8000
echo API Docs:    http://localhost:8000/docs
echo WebSocket:   ws://localhost:8000/ws/updates
echo.
echo.
echo Press any key to stop services...
pause

REM Stop services
taskkill /F /IM python.exe >nul 2>nul
taskkill /F /IM node.exe >nul 2>nul

echo Services stopped
