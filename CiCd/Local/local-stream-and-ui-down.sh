#!/usr/bin/env bash
# Stop host Stream + Vite UI started by local-stream-and-ui-up.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

WEB_PID_FILE="$ROOT/.local-run/web.pid"

echo "Stopping Vite UI…"
if [[ -f "$WEB_PID_FILE" ]]; then
  pid="$(cat "$WEB_PID_FILE")"
  if kill -0 "$pid" 2>/dev/null; then
    kill "$pid" 2>/dev/null || true
    # vite often spawns children — also match the bound port process
    sleep 0.3
  else
    echo "Stale web pid file (process $pid not running)"
  fi
  rm -f "$WEB_PID_FILE"
fi
if command -v pkill >/dev/null 2>&1; then
  pkill -f "vite --host 127.0.0.1 --port 5173" 2>/dev/null || true
  pkill -f "vite.*5173" 2>/dev/null || true
fi
if curl -sf "http://127.0.0.1:5173/" >/dev/null 2>&1; then
  echo "Warning: something still responds on :5173" >&2
else
  echo "Vite UI stopped"
fi

echo "Stopping local Stream…"
bash "$ROOT/CiCd/Local/local-down.sh"

echo "local:stream-and-ui-down complete."
