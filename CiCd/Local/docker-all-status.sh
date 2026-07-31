#!/usr/bin/env bash
# Status for dependency containers + host app health.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "=== Dependency containers (Docker) ==="
services="$(docker compose -f docker-compose.local.yml config --services 2>/dev/null || true)"
if [[ -z "${services// }" ]]; then
  echo "(none defined in docker-compose.local.yml)"
else
  docker compose -f docker-compose.local.yml ps
fi

echo ""
echo "=== Host application ==="
if curl -sf "http://127.0.0.1:8787/health" >/dev/null 2>&1; then
  echo "local-stream: $(curl -sf http://127.0.0.1:8787/health)"
else
  echo "local-stream: down  (npm run local:up)"
fi
if curl -sf "http://127.0.0.1:5173/" >/dev/null 2>&1; then
  echo "web (vite):   up on :5173"
else
  echo "web (vite):   down  (npm run local:web)"
fi
