"""CLI: python -m patient_risk_assessment_agent \"question\"."""

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
from patient_risk_assessment_agent.prompts import SYSTEM_PROMPT


def main() -> int:
    return main_for_agent(
        agent_title="Patient Risk Assessment Agent",
        system_prompt=SYSTEM_PROMPT,
        package_root=_PKG_ROOT,
    )


if __name__ == "__main__":
    raise SystemExit(main())
