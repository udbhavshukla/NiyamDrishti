@echo off
echo ===================================================
echo   NiyamDrishti AI - Local Setup & Initialization
echo ===================================================
echo.

echo [1/4] Setting up Python Virtual Environment...
cd backend
if not exist venv (
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Python 3 not found or failed to create venv. Please ensure Python 3.10+ is installed.
        pause
        exit /b 1
    )
)

call venv\Scripts\activate.bat
echo [2/4] Installing Backend Dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install backend dependencies.
    pause
    exit /b 1
)

echo [3/4] Initializing and Seeding Database...
set PYTHONPATH=.
python -c "from app.database import create_tables; from app.seed_rules import seed_rules; create_tables(); seed_rules(); print('[OK] Database and 15 Legal Metrology rules initialized.')"

echo.
echo [4/4] Installing Frontend Node Dependencies...
cd ..\frontend
where npm >nul 2>nul
if %errorlevel% equ 0 (
    call npm install
) else (
    echo [NOTE] npm/Node.js is not found on PATH. Backend setup is complete; install Node.js 18+ to run the React web frontend.
)

cd ..
echo.
echo ===================================================
echo   Setup Complete!
echo   To launch the system, run: start_demo.bat
echo ===================================================
pause
