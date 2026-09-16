#!/usr/bin/env bash
set -e
echo "==================================================="
echo "  NiyamDrishti AI - Local Setup & Initialization   "
echo "==================================================="

echo "[1/4] Setting up Python Virtual Environment..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

echo "[2/4] Installing Backend Dependencies..."
pip install -r requirements.txt

echo "[3/4] Initializing and Seeding Database..."
export PYTHONPATH=.
python -c "from app.database import create_tables; from app.seed_rules import seed_rules; create_tables(); seed_rules(); print('[OK] Database and 15 Legal Metrology rules initialized.')"

echo "[4/4] Installing Frontend Node Dependencies..."
cd ../frontend
if command -v npm >/dev/null 2>&1; then
    npm install
else
    echo "[NOTE] npm/Node.js is not found on PATH. Backend setup is complete; install Node.js 18+ to run the React web frontend."
fi

cd ..
echo "==================================================="
echo "  Setup Complete!"
echo "  To launch the system, run: ./start_demo.sh"
echo "==================================================="
