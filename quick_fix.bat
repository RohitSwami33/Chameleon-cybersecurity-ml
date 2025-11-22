@echo off
echo ========================================
echo Chameleon Quick Fix Script
echo ========================================
echo.

echo Step 1: Fixing NumPy version...
cd Backend
pip install "numpy<2.0" --quiet
echo NumPy fixed!
echo.

echo Step 2: Checking MongoDB...
mongo --version >nul 2>&1
if %errorlevel% equ 0 (
    echo MongoDB is installed!
    echo Please make sure MongoDB is running:
    echo   - Run: mongod --dbpath="C:\data\db"
    echo   - Or: net start MongoDB
) else (
    echo MongoDB is NOT installed!
    echo.
    echo Please install MongoDB:
    echo   1. Download from: https://www.mongodb.com/try/download/community
    echo   2. Or use MongoDB Atlas (cloud): https://www.mongodb.com/cloud/atlas
)
echo.

echo Step 3: Installation complete!
echo.
echo Next steps:
echo   1. Make sure MongoDB is running
echo   2. Restart the backend: cd Backend ^&^& uvicorn main:app --reload
echo   3. Open frontend: http://localhost:5173/
echo.
pause
