#!/usr/bin/env bash
set -e

echo "=== Starting BharatPay in Development Mode ==="

# 1. Activate or create virtualenv for backend
cd "$(dirname "$0")"

if [ ! -d "backend/venv" ]; then
    echo "[Dev] Creating Python virtual environment..."
    python3 -m venv backend/venv
    backend/venv/bin/pip install --upgrade pip
    backend/venv/bin/pip install -r backend/requirements.txt
fi

echo "[Dev] Starting FastAPI backend on http://localhost:8000 ..."
(cd backend && ./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload) &
BACKEND_PID=$!

echo "[Dev] Starting React Vite frontend on http://localhost:5173 ..."
(cd frontend && npm install && npm run dev) &
FRONTEND_PID=$!

cleanup() {
    echo "Stopping dev servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "BharatPay dev environment is running!"
echo "- Backend:  http://localhost:8000"
echo "- Frontend: http://localhost:5173"
echo "Press Ctrl+C to stop."

wait
