#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR/backend"
. .venv/bin/activate
python -m app.bootstrap
exec uvicorn app.main:app --reload --port 8000
