#!/usr/bin/env bash
# Stop dependency containers only (does not stop host stream/web).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "Stopping local dependency containers…"
docker compose -f docker-compose.local.yml down
echo "Dependency containers stopped."
echo "Host app (if running): kill \$(cat .local-run/stream.pid)  # or npm run local:down"
