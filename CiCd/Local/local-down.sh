#!/usr/bin/env bash
# Stop host local-stream (application). Does not touch Docker deps.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

PID_FILE="$ROOT/.local-run/stream.pid"
if [[ -f "$PID_FILE" ]]; then
  pid="$(cat "$PID_FILE")"
  if kill -0 "$pid" 2>/dev/null; then
    # stream-dev.sh exec's uvicorn — kill process group if possible
    kill "$pid" 2>/dev/null || true
    # also stop anything still bound to 8787 from this tree
    if command -v pkill >/dev/null 2>&1; then
      pkill -f "uvicorn local.stream_app:app" 2>/dev/null || true
    fi
    echo "Stopped host local-stream (pid $pid)"
  else
    echo "Stale pid file (process $pid not running)"
  fi
  rm -f "$PID_FILE"
else
  if command -v pkill >/dev/null 2>&1; then
    pkill -f "uvicorn local.stream_app:app" 2>/dev/null && echo "Stopped host local-stream" || echo "local-stream not running"
  else
    echo "No .local-run/stream.pid — local-stream may not be running"
  fi
fi
