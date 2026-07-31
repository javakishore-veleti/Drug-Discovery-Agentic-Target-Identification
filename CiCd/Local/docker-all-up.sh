#!/usr/bin/env bash
# Start dependency containers only (never the app).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

COMPOSE=(docker compose -f docker-compose.local.yml)
services="$("${COMPOSE[@]}" config --services 2>/dev/null || true)"
if [[ -z "${services// }" ]]; then
  echo "No dependency services defined in docker-compose.local.yml."
  echo "App stays on the host — nothing to start in Docker for V1 local mode."
  echo "Next: npm run local:up && npm run local:web"
  exit 0
fi

echo "Starting local dependency containers…"
"${COMPOSE[@]}" up -d
"${COMPOSE[@]}" ps
echo ""
echo "Deps are up. Start the app on the host:"
echo "  npm run local:up"
echo "  npm run local:web"
