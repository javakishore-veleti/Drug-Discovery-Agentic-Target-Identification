"""CLI: python -m drug_design_hypothesis_agent \"question\"."""

from __future__ import annotations

import sys
from pathlib import Path

# agents/ → framework; this agent dir → package
_PKG_ROOT = Path(__file__).resolve().parents[1]
_AGENTS = _PKG_ROOT.parent
for _p in (_AGENTS, _PKG_ROOT):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from framework.cli import main_for_agent
from drug_design_hypothesis_agent.prompts import SYSTEM_PROMPT


def main() -> int:
    return main_for_agent(
        agent_title="Drug Design Hypothesis Agent",
        system_prompt=SYSTEM_PROMPT,
        package_root=_PKG_ROOT,
    )


if __name__ == "__main__":
    raise SystemExit(main())
