#!/usr/bin/env bash
echo "==================================================="
echo "  NiyamDrishti AI - Starting Live Demo Servers     "
echo "==================================================="

echo "Starting Backend API Server (Port 8000)..."
(cd backend && source venv/bin/activate && export PYTHONPATH=. && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000) &
BACKEND_PID=$!

sleep 3

echo "Starting Frontend Web Portal (Port 5173)..."
(cd frontend && npm run dev -- --host 127.0.0.1 --port 5173) &
FRONTEND_PID=$!

echo ""
echo "==================================================="
echo "  Both services are running!"
echo "  - Web Portal:   http://127.0.0.1:5173"
echo "  - Swagger Docs: http://127.0.0.1:8000/docs"
echo "  - Login ID:     LMO-DEL-2024-884"
echo "  - Security PIN: 8842"
echo "  Press Ctrl+C to terminate both servers."
echo "==================================================="

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" SIGINT SIGTERM
wait
