#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

cd "$ROOT_DIR/backend"
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp -n .env.example .env || true
python -m app.bootstrap

echo "[OK] Backend bootstrap complete"

echo "[INFO] Frontend dependencies"
cd "$ROOT_DIR/frontend"
npm install
cp -n .env.example .env || true

echo "[OK] Frontend bootstrap complete"
