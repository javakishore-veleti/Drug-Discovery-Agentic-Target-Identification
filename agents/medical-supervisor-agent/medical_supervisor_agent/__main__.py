"""CLI: python -m medical_supervisor_agent \"question\"."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_PKG_ROOT = Path(__file__).resolve().parents[1]
_AGENTS = _PKG_ROOT.parent
for _p in (_AGENTS, _PKG_ROOT):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from framework.base_agent import run_prompt
from framework.cli import load_agent_env
from framework.config import get_aws_region, get_bedrock_model_id

from medical_supervisor_agent.agent import create_agent


def main() -> int:
    load_agent_env(_PKG_ROOT)
    parser = argparse.ArgumentParser(description="Medical Supervisor (local stub)")
    parser.add_argument("prompt", nargs="+")
    args = parser.parse_args()
    prompt = " ".join(args.prompt).strip()
    if not prompt:
        print("Provide a non-empty prompt", file=sys.stderr)
        return 2
    print("agent=Medical Supervisor (local stub)", file=sys.stderr)
    print(f"model={get_bedrock_model_id()} region={get_aws_region()}", file=sys.stderr)
    print("mode=local_cli — NOT AgentCore Runtime multi-agent", file=sys.stderr)
    print(run_prompt(create_agent(), prompt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
