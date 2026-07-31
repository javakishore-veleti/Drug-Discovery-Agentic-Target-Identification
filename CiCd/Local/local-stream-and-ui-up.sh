#!/usr/bin/env bash
# Start host Stream + Vite UI in the background (paired with local-stream-and-ui-down).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
mkdir -p "$ROOT/.local-run"

bash "$ROOT/CiCd/Local/local-up.sh"

WEB_PID_FILE="$ROOT/.local-run/web.pid"
WEB_LOG="$ROOT/.local-run/web.log"

if curl -sf "http://127.0.0.1:5173/" >/dev/null 2>&1; then
  echo "Vite UI already up on :5173"
else
  # Stop stale tracked UI if any
  if [[ -f "$WEB_PID_FILE" ]]; then
    old="$(cat "$WEB_PID_FILE")"
    kill "$old" 2>/dev/null || true
    rm -f "$WEB_PID_FILE"
  fi
  echo "Starting Vite UI on :5173 (background)…"
  nohup npm --prefix web run dev -- --host 127.0.0.1 --port 5173 \
    >"$WEB_LOG" 2>&1 &
  echo $! >"$WEB_PID_FILE"
  ready=
  for _ in $(seq 1 60); do
    if curl -sf "http://127.0.0.1:5173/" >/dev/null 2>&1; then
      echo "Vite UI ready"
      ready=1
      break
    fi
    sleep 0.5
  done
  if [[ -z "${ready}" ]]; then
    echo "Vite UI failed to become ready — see .local-run/web.log" >&2
    exit 1
  fi
fi

echo ""
echo "Local stack is up:"
echo "  Stream: http://127.0.0.1:8787/health"
echo "  UI:     http://127.0.0.1:5173/"
echo "Stop both: npm run local:stream-and-ui-down"
