@echo off
echo ===================================================
echo   NiyamDrishti AI - Starting Live Demo Servers
echo ===================================================
echo.

echo Starting Backend API Server (Port 8000)...
start "NiyamDrishti Backend API (:8000)" cmd /k "cd backend && call venv\Scripts\activate.bat && set PYTHONPATH=. && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak >nul

echo Starting Frontend Web Portal (Port 5173)...
start "NiyamDrishti Frontend Portal (:5173)" cmd /k "cd frontend && npm run dev -- --host 127.0.0.1 --port 5173"

echo.
echo ===================================================
echo   Both services are starting!
echo   - Web Portal:   http://127.0.0.1:5173
echo   - Swagger Docs: http://127.0.0.1:8000/docs
echo   - Login ID:     LMO-DEL-2024-884
echo   - Security PIN: 8842
echo ===================================================
echo.
