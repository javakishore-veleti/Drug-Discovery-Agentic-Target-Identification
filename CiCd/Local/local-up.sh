#!/usr/bin/env bash
# Start host local-stream (application — not Docker) + ensure web/.env.local.
# Always syncs the uv venv from requirements before (re)starting Stream.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

STAMP_FILE="$ROOT/.local-run/requirements.sha256"

# Optional Docker deps first (no-op when compose has no services)
bash "$ROOT/CiCd/Local/docker-all-up.sh"

# Always create/sync Python env (picks up new libraries in requirements.txt)
bash "$ROOT/CiCd/Local/ensure-python-env.sh"
LOCAL_PYTHON_VENV="$(cat "$ROOT/.local-run/python-venv")"
export LOCAL_PYTHON_VENV

req_hash=""
if [[ -f "$STAMP_FILE" ]]; then
  req_hash="$(cat "$STAMP_FILE")"
fi
prev_hash=""
if [[ -f "$ROOT/.local-run/stream.requirements.sha256" ]]; then
  prev_hash="$(cat "$ROOT/.local-run/stream.requirements.sha256")"
fi

stream_healthy=0
if curl -sf "http://127.0.0.1:8787/health" >/dev/null 2>&1; then
  stream_healthy=1
fi

need_restart=0
if [[ "$stream_healthy" -eq 0 ]]; then
  need_restart=1
elif [[ -n "$req_hash" && "$req_hash" != "$prev_hash" ]]; then
  echo "requirements.txt changed since Stream start — restarting host Stream…"
  need_restart=1
fi

if [[ "$need_restart" -eq 1 ]]; then
  bash "$ROOT/CiCd/Local/local-down.sh" >/dev/null 2>&1 || true
  echo "Starting host local-stream on :8787…"
  mkdir -p "$ROOT/.local-run"
  nohup env LOCAL_PYTHON_VENV="$LOCAL_PYTHON_VENV" bash "$ROOT/CiCd/Local/stream-dev.sh" \
    >"$ROOT/.local-run/stream.log" 2>&1 &
  echo $! >"$ROOT/.local-run/stream.pid"
  ready=
  for _ in $(seq 1 60); do
    if curl -sf "http://127.0.0.1:8787/health" >/dev/null 2>&1; then
      echo "local-stream ready"
      ready=1
      break
    fi
    sleep 0.5
  done
  if [[ -z "${ready}" ]]; then
    echo "local-stream failed to become healthy — see .local-run/stream.log" >&2
    exit 1
  fi
  if [[ -n "$req_hash" ]]; then
    printf '%s\n' "$req_hash" >"$ROOT/.local-run/stream.requirements.sha256"
  fi
else
  echo "local-stream already healthy on :8787 (requirements unchanged)"
fi

# Always force local UI mode for local:up (preserve prior AWS env once).
ENV_LOCAL="$ROOT/web/.env.local"
ENV_EXAMPLE="$ROOT/web/.env.local.example"
if [[ -f "$ENV_LOCAL" ]] && ! grep -q '^VITE_STACK_MODE=local' "$ENV_LOCAL" 2>/dev/null; then
  cp "$ENV_LOCAL" "$ROOT/web/.env.local.aws.bak"
  echo "Backed up non-local web/.env.local → web/.env.local.aws.bak"
fi
cp "$ENV_EXAMPLE" "$ENV_LOCAL"
echo "Wrote web/.env.local (VITE_STACK_MODE=local → host Stream :8787)"

echo ""
echo "App is on the host (not in Docker)."
echo "  Venv:   $LOCAL_PYTHON_VENV"
echo "  Stream: http://127.0.0.1:8787/health"
echo "  UI:     npm run local:web"
echo "  Stop:   npm run local:down"

