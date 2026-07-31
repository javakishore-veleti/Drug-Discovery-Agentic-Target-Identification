#!/usr/bin/env bash
# Ensure host Python venv via uv and sync requirements (idempotent, fast).
# Venv path: ~/runtime_data/python_venvs/drug-discovery-agentic-td
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
URA="$ROOT/agents/unified-research-agent"
REQ="${LOCAL_PYTHON_REQUIREMENTS:-$URA/requirements.txt}"
VENV_DIR="${LOCAL_PYTHON_VENV:-$HOME/runtime_data/python_venvs/drug-discovery-agentic-td}"
PY_VER="${LOCAL_PYTHON_VERSION:-3.12}"
STAMP_DIR="$ROOT/.local-run"
STAMP_FILE="$STAMP_DIR/requirements.sha256"
VENV_LINK="$STAMP_DIR/python-venv"

if [[ ! -f "$REQ" ]]; then
  echo "requirements not found: $REQ" >&2
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required for local Python env management." >&2
  echo "Install: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
  exit 1
fi

mkdir -p "$(dirname "$VENV_DIR")" "$STAMP_DIR"

if [[ ! -x "$VENV_DIR/bin/python" ]]; then
  echo "Creating uv venv ($PY_VER) at $VENV_DIR …"
  uv venv "$VENV_DIR" --python "$PY_VER"
else
  echo "Using venv: $VENV_DIR"
fi

echo "Syncing requirements with uv → $REQ"
uv pip install --python "$VENV_DIR/bin/python" -r "$REQ"

# Stamp + pointer for other scripts
if command -v shasum >/dev/null 2>&1; then
  shasum -a 256 "$REQ" | awk '{print $1}' >"$STAMP_FILE"
elif command -v sha256sum >/dev/null 2>&1; then
  sha256sum "$REQ" | awk '{print $1}' >"$STAMP_FILE"
fi
printf '%s\n' "$VENV_DIR" >"$VENV_LINK"

export LOCAL_PYTHON_VENV="$VENV_DIR"
echo "Python: $("$VENV_DIR/bin/python" -V) @ $VENV_DIR"
