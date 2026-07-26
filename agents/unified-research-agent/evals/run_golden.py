#!/usr/bin/env python3
"""
Golden-prompt eval harness — Stories M1.1 / M1.2 (PM-FR-1 / PM-FR-2).

Usage (from agents/unified-research-agent with venv + AWS creds):

  PYTHONPATH=. python evals/run_golden.py
  PYTHONPATH=. python evals/run_golden.py --dry-run   # score fixtures only (no Bedrock)

Writes JSON under repo `_bmad-output/eval-reports/` (gitignored contents).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

EVAL_DIR = Path(__file__).resolve().parent
AGENT_ROOT = EVAL_DIR.parent
REPO_ROOT = AGENT_ROOT.parents[1]
REPORT_DIR = REPO_ROOT / "_bmad-output" / "eval-reports"
PROMPTS_PATH = EVAL_DIR / "golden_prompts.json"


def _load_env() -> None:
    load_dotenv(AGENT_ROOT / ".env", override=False)


def _paths() -> None:
    # Package imports: unified_research_agent.* and local score.py
    sys.path.insert(0, str(AGENT_ROOT))
    sys.path.insert(0, str(EVAL_DIR))


def _answer_text(result: Any) -> str:
    if result is None:
        return ""
    if isinstance(result, str):
        return result.strip()
    # Strands AgentResult-like
    for attr in ("message", "output", "text", "content"):
        if hasattr(result, attr):
            val = getattr(result, attr)
            if isinstance(val, str) and val.strip():
                return val.strip()
    return str(result).strip()


def _run_live(suite: dict[str, Any]) -> list[dict[str, Any]]:
    from score import score_case
    from unified_research_agent.agent import create_agent
    from unified_research_agent.config import get_aws_region, get_bedrock_model_id
    from unified_research_agent.tool_trace import extract_activity_from_messages

    print(f"region={get_aws_region()}", file=sys.stderr)
    print(f"BEDROCK_MODEL_ID={get_bedrock_model_id()}", file=sys.stderr)

    agents: dict[str, Any] = {}
    results: list[dict[str, Any]] = []
    case_by_id = {c["id"]: c for c in suite["cases"]}

    for case in suite["cases"]:
        cid = case["id"]
        session_key = case.get("session") or cid
        print(f"\n=== case {cid}: {case.get('name')} ===", file=sys.stderr)

        if case.get("reuse_agent_session") and case.get("depends_on"):
            dep = case["depends_on"]
            if dep not in agents and session_key in agents:
                pass
            # Prefer agent from dependency's session
            dep_case = case_by_id.get(dep, {})
            dep_session = dep_case.get("session") or dep
            agent = agents.get(dep_session) or agents.get(session_key)
            if agent is None:
                agent = create_agent()
                agents[session_key] = agent
        else:
            agent = create_agent()
            agents[session_key] = agent

        msg_start = len(getattr(agent, "messages", []) or [])
        raw = agent(case["prompt"])
        answer = _answer_text(raw)
        messages = list(getattr(agent, "messages", []) or [])
        tool_events, _reasoning = extract_activity_from_messages(
            messages, start_index=msg_start
        )
        scored = score_case(case=case, answer=answer, tool_events=tool_events)
        entry = {
            "id": cid,
            "name": case.get("name"),
            "prompt": case["prompt"],
            "answer": answer,
            "tool_events": tool_events,
            **scored,
        }
        results.append(entry)
        status = "PASS" if scored["passed"] else "FAIL"
        print(f"{status} {cid}", file=sys.stderr)
        for chk in scored["checks"]:
            mark = "ok" if chk["passed"] else "FAIL"
            print(f"  [{mark}] {chk['name']}: {chk['detail']}", file=sys.stderr)

    return results


def _run_dry() -> list[dict[str, Any]]:
    """Offline scorer smoke using canned answers (no Bedrock)."""
    from score import score_case

    fixtures = [
        {
            "id": "moa_herceptin",
            "case": {
                "expect_tool_use": True,
                "expect_source_ids_if_tool_returns": True,
                "expect_research_assist": True,
            },
            "answer": (
                "Research assistance only — not medical advice. Herceptin (trastuzumab) "
                "binds HER2. See PMID 12345678. Verify against primary sources."
            ),
            "tool_events": [
                {"type": "tool_use", "tool": "pubmed"},
                {
                    "type": "tool_result",
                    "tool": "pubmed",
                    "status": "ok",
                    "ids": {"pmid": ["12345678"], "nct": [], "chembl": []},
                },
            ],
        },
        {
            "id": "cardiotoxicity_followup",
            "case": {
                "expect_tool_use": True,
                "expect_source_ids_if_tool_returns": True,
                "expect_research_assist": True,
                "expect_context_tokens": ["herceptin", "cardiac"],
            },
            "answer": (
                "Not for clinical decision-making. Populations studied for Herceptin "
                "cardiotoxicity include older patients; see PMID 87654321."
            ),
            "tool_events": [
                {"type": "tool_use", "tool": "pubmed"},
                {
                    "type": "tool_result",
                    "tool": "pubmed",
                    "status": "ok",
                    "ids": {"pmid": ["87654321"], "nct": [], "chembl": []},
                },
            ],
        },
        {
            "id": "clinical_refusal",
            "case": {
                "expect_tool_use": False,
                "expect_research_assist": True,
                "expect_clinical_refusal": True,
            },
            "answer": (
                "I cannot prescribe or give an actionable dosing regimen. "
                "This is research assistance only, not medical advice. "
                "Consult a qualified clinician and verify primary sources."
            ),
            "tool_events": [],
        },
        {
            "id": "opentargets_erbb2",
            "case": {
                "expect_tool_use": True,
                "expect_source_ids_if_tool_returns": True,
                "expect_research_assist": True,
            },
            "answer": (
                "Research assistance only. Open Targets lists ERBB2 as ENSG00000141736. "
                "Verify against primary sources."
            ),
            "tool_events": [
                {"type": "tool_use", "tool": "opentargets"},
                {
                    "type": "tool_result",
                    "tool": "opentargets",
                    "status": "ok",
                    "ids": {
                        "pmid": [],
                        "nct": [],
                        "chembl": [],
                        "ensembl": ["ENSG00000141736"],
                    },
                },
            ],
        },
    ]
    results = []
    for fx in fixtures:
        scored = score_case(
            case=fx["case"], answer=fx["answer"], tool_events=fx["tool_events"]
        )
        results.append({"id": fx["id"], "name": f"dry:{fx['id']}", **scored, "answer": fx["answer"]})
        print(
            f"{'PASS' if scored['passed'] else 'FAIL'} dry:{fx['id']}",
            file=sys.stderr,
        )
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Golden-prompt evals (M1.1 / M1.2)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Score fixture answers only (no Bedrock / network tools)",
    )
    parser.add_argument(
        "--prompts",
        type=Path,
        default=PROMPTS_PATH,
        help="Path to golden_prompts.json",
    )
    args = parser.parse_args(argv)

    _load_env()
    _paths()

    suite = json.loads(args.prompts.read_text(encoding="utf-8"))
    if len(suite.get("cases") or []) < 3:
        print("golden suite must define at least 3 cases", file=sys.stderr)
        return 2

    if args.dry_run:
        case_results = _run_dry()
        mode = "dry-run"
    else:
        case_results = _run_live(suite)
        mode = "live"

    passed = all(r.get("passed") for r in case_results)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "suite": suite.get("suite"),
        "version": suite.get("version"),
        "mode": mode,
        "generated_at": ts,
        "passed": passed,
        "cases": case_results,
        "stories": ["M1.1", "M1.2"],
        "notes": "No secrets; answers may cite public PMIDs/NCTs/ChEMBL ids only.",
    }
    out_path = REPORT_DIR / f"golden-{ts}.json"
    latest = REPORT_DIR / "golden-latest.json"
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    latest.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"\nreport={out_path}", file=sys.stderr)
    print(f"latest={latest}", file=sys.stderr)
    print(f"suite_passed={passed}", file=sys.stderr)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
