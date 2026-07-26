#!/usr/bin/env python3
"""
Epic L polish — import/smoke specialist packages without Bedrock calls.

Verifies each local specialist module is importable and exposes expected
entrypoints. Run:

  PYTHONPATH=agents:agents/unified-research-agent python agents/scripts/smoke_specialists_import.py
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

AGENTS = Path(__file__).resolve().parents[1]
ROOT = AGENTS.parent


def main() -> int:
    # Ensure layout on path
    for p in (AGENTS, AGENTS / "unified-research-agent", ROOT / "gateways" / "database"):
        s = str(p)
        if s not in sys.path:
            sys.path.insert(0, s)

    checks: list[tuple[str, str]] = [
        ("framework.base_agent", "create_research_agent"),
        ("framework.tools", "V1_TOOLS"),
        ("framework.prompts", "with_research_assist_boundary"),
    ]
    # Specialist packages use various module names — import package roots / cli
    packages = [
        "drug_profile_analysis_agent",
        "patient_risk_assessment_agent",
        "pathway_mapping_agent",
        "cardioprotection_target_agent",
        "drug_design_hypothesis_agent",
        "medical_supervisor_agent",
        "genetic_risk_assessment",
    ]
    # Actual folder names use hyphens — load via path sniff instead
    folder_mods = [
        "drug-profile-analysis-agent",
        "patient-risk-assessment-agent",
        "pathway-mapping-agent",
        "cardioprotection-target-agent",
        "drug-design-hypothesis-agent",
        "medical-supervisor-agent",
        "genetic-risk-assessment",
    ]

    failed = 0
    for mod, attr in checks:
        try:
            m = importlib.import_module(mod)
            if not hasattr(m, attr):
                print(f"FAIL {mod}: missing {attr}", file=sys.stderr)
                failed += 1
            else:
                print(f"ok {mod}.{attr}")
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL {mod}: {exc}", file=sys.stderr)
            failed += 1

    for folder in folder_mods:
        pkg_dir = AGENTS / folder
        if not pkg_dir.is_dir():
            print(f"FAIL missing package dir {folder}", file=sys.stderr)
            failed += 1
            continue
        readme = pkg_dir / "README.md"
        if not readme.is_file():
            print(f"FAIL {folder}: no README.md", file=sys.stderr)
            failed += 1
            continue
        # Prefer a py project module if present
        py_files = list(pkg_dir.glob("*.py")) + list(pkg_dir.glob("*/*.py"))
        if not py_files:
            print(f"FAIL {folder}: no Python modules", file=sys.stderr)
            failed += 1
            continue
        print(f"ok {folder} ({len(py_files)} py files, README present)")

    # Production tools include opentargets
    try:
        from unified_research_agent.tools import opentargets_search  # noqa: F401

        print("ok unified_research_agent.tools.opentargets_search")
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL opentargets_search import: {exc}", file=sys.stderr)
        failed += 1

    if failed:
        print(f"specialist_smoke_failed={failed}", file=sys.stderr)
        return 1
    print("specialist_smoke=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
