@echo off
echo ========================================
echo Chameleon Build Script
echo ========================================
echo.

echo [1/2] Building Frontend...
cd frontend
call npm run build
if errorlevel 1 (
    echo ERROR: Frontend build failed!
    cd ..
    pause
    exit /b 1
)
cd ..
echo ✓ Frontend built successfully
echo.

echo [2/2] Backend Check...
echo Backend is Python-based and runs from source
echo No build step required
echo ✓ Backend ready
echo.

echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Frontend Output: frontend/dist/
echo Backend Source: Backend/
echo.
echo To deploy:
echo 1. Deploy frontend/dist/ to your web server
echo 2. Run backend with: cd Backend ^&^& uvicorn main:app --host 0.0.0.0 --port 8000
echo.
pause
