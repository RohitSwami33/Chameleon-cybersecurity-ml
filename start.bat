@echo off
echo Starting Chameleon Adaptive Deception System...
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Starting Backend Server...
start "Chameleon Backend" cmd /k "cd Backend && uvicorn main:app --reload"

echo Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

echo Starting Frontend Server...
start "Chameleon Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Both servers are starting!
echo.
echo Backend API: http://localhost:8000
echo Frontend App: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo Login: admin / chameleon2024
echo.
pause
