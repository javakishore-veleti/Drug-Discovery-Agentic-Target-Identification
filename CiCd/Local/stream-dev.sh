#!/usr/bin/env bash
# Run local Stream API on the host (no Docker) — still no Cognito.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
URA="$ROOT/agents/unified-research-agent"
cd "$ROOT"

# Prefer shared home venv; create/sync if missing
if [[ -z "${LOCAL_PYTHON_VENV:-}" ]]; then
  if [[ -f "$ROOT/.local-run/python-venv" ]]; then
    LOCAL_PYTHON_VENV="$(cat "$ROOT/.local-run/python-venv")"
  else
    LOCAL_PYTHON_VENV="$HOME/runtime_data/python_venvs/drug-discovery-agentic-td"
  fi
fi
if [[ ! -x "${LOCAL_PYTHON_VENV}/bin/python" ]]; then
  bash "$ROOT/CiCd/Local/ensure-python-env.sh"
  LOCAL_PYTHON_VENV="$(cat "$ROOT/.local-run/python-venv")"
fi

# Root + agents/ (framework + specialists) + unified-research-agent
export PYTHONPATH="$ROOT:$ROOT/agents:$URA${PYTHONPATH:+:$PYTHONPATH}"
if [[ -f "$URA/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$URA/.env"
  set +a
fi

# Local cost-saving path: always use in-process adapters (PubMed/CT/ChEMBL/OT),
# never AgentCore Gateway MCP — even if URA .env still has a destroyed Gateway URL.
export USE_GATEWAY_TOOLS=false
unset AGENTCORE_GATEWAY_URL || true

exec "${LOCAL_PYTHON_VENV}/bin/python" -m uvicorn local.stream_app:app \
  --host 127.0.0.1 --port 8787 --reload
