#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_LOG="/tmp/happyellie_backend.log"
FRONTEND_LOG="/tmp/happyellie_frontend.log"

cleanup() {
  if [[ -n "${BACKEND_PID:-}" ]]; then kill "$BACKEND_PID" >/dev/null 2>&1 || true; fi
  if [[ -n "${FRONTEND_PID:-}" ]]; then kill "$FRONTEND_PID" >/dev/null 2>&1 || true; fi
}
trap cleanup EXIT INT TERM

cd "$ROOT_DIR/backend"
. .venv/bin/activate
python -m app.bootstrap >/dev/null
uvicorn app.main:app --port 8000 > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!

cd "$ROOT_DIR/frontend"
npm run dev -- --host 127.0.0.1 --port 5173 > "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!

sleep 3

echo "[OK] HappyEllie backend: http://127.0.0.1:8000"
echo "[OK] HappyEllie frontend: http://127.0.0.1:5173"
echo "[INFO] Logs: $BACKEND_LOG and $FRONTEND_LOG"

wait "$FRONTEND_PID"
