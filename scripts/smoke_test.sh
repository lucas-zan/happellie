#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR/backend"
. .venv/bin/activate
python -m app.bootstrap
uvicorn app.main:app --port 8010 > /tmp/happyellie_smoke.log 2>&1 &
PID=$!
trap 'kill $PID >/dev/null 2>&1 || true' EXIT
sleep 2

curl -sf http://127.0.0.1:8010/api/v1/health >/dev/null
curl -sf -X POST http://127.0.0.1:8010/api/v1/lessons/next \
  -H 'Content-Type: application/json' \
  -d '{"student_id":"student-demo","requested_vocab":[],"lesson_type":"pet_feeding","level_hint":"starter"}' >/dev/null
curl -sf -X POST http://127.0.0.1:8010/api/v1/sessions/complete \
  -H 'Content-Type: application/json' \
  -d '{"student_id":"student-demo","lesson_id":"lesson-test","duration_seconds":120,"total_score":40,"earned_food":2,"earned_coins":3,"block_results":[{"block_id":"b1","block_type":"vocab_intro","correct":true,"score":10,"duration_ms":1000},{"block_id":"b2","block_type":"audio_choice","correct":true,"score":20,"duration_ms":1200}]}' >/dev/null
curl -sf http://127.0.0.1:8010/api/v1/pets/student-demo >/dev/null
curl -sf http://127.0.0.1:8010/api/v1/profiles/student-demo >/dev/null
curl -sf http://127.0.0.1:8010/api/v1/admin/overview >/dev/null

echo "[OK] Backend smoke test passed"
