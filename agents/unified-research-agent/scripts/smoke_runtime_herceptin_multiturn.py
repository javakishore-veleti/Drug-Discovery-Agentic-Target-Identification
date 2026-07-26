#!/usr/bin/env python3
"""
Story 3.3 — Herceptin multi-turn Runtime smoke (mechanism → cardiotoxicity).

Same runtimeSessionId for both turns. Turn 2 must stay in Herceptin/HER2 context
without restating the drug name (FR10, FR17). Research-assist boundary held (FR12).
Source IDs (PMID / NCT / ChEMBL) checked when present in answers (FR11).
"""

from __future__ import annotations

import json
import os
import re
import sys
import uuid

import boto3

TURN1 = "What is the mechanism of action of Herceptin?"
TURN2 = (
    "Which patient populations are most vulnerable to its cardiotoxicity?"
)

# Continuity signals for turn 2 (drug name not restated in the user prompt).
_HER2_CONTEXT = re.compile(
    r"\b(herceptin|trastuzumab|her2|erbb2|anti[- ]?her2)\b",
    re.I,
)
# Allow markdown between label and id: PMID **17229773**, PMID: 17229773
_PMID = re.compile(r"\bPMID\b[:\s*_]*([0-9]{5,9})\b", re.I)
_NCT = re.compile(r"\bNCT\d{8}\b", re.I)
_CHEMBL = re.compile(r"\bCHEMBL\d+\b", re.I)

# Soft research-assist red flags (should not appear as actionable orders).
_CLINICAL_ORDER = re.compile(
    r"\b(prescribe|start the patient on|dose the patient|"
    r"administer\s+\d+\s*mg|take\s+\d+\s*mg)\b",
    re.I,
)


def _invoke(client, arn: str, session: str, prompt: str) -> dict:
    payload = json.dumps({"input": {"prompt": prompt}})
    resp = client.invoke_agent_runtime(
        agentRuntimeArn=arn,
        runtimeSessionId=session,
        payload=payload,
        qualifier="DEFAULT",
        contentType="application/json",
        accept="application/json",
    )
    body = resp["response"].read().decode()
    print(f"--- turn prompt={prompt!r}", file=sys.stderr)
    print(body)
    return json.loads(body)


def _text(turn: dict) -> str:
    return (turn.get("response") or turn.get("output", {}).get("message") or "").strip()


def _source_ids(text: str) -> dict[str, list[str]]:
    return {
        "pmid": sorted(set(_PMID.findall(text))),
        "nct": sorted(set(_NCT.findall(text))),
        "chembl": sorted(set(m.upper() for m in _CHEMBL.findall(text))),
    }


def main() -> int:
    arn = os.environ.get("AGENT_RUNTIME_ARN", "").strip()
    if not arn:
        print("Set AGENT_RUNTIME_ARN", file=sys.stderr)
        return 2
    region = (
        os.environ.get("AWS_REGION")
        or os.environ.get("AWS_DEFAULT_REGION")
        or "us-east-1"
    )
    session = "smoke-herc-" + uuid.uuid4().hex
    if len(session) < 33:
        session = session.ljust(33, "0")

    client = boto3.client("bedrock-agentcore", region_name=region)
    print(f"runtime={arn}", file=sys.stderr)
    print(f"session={session}", file=sys.stderr)

    turn1 = _invoke(client, arn, session, TURN1)
    out1 = turn1.get("output") or {}
    text1 = _text(turn1)
    if out1.get("status") == "error" or turn1.get("status") not in (None, "success"):
        # status on outer body is "success" for our runtime_app
        pass
    if turn1.get("status") != "success" or not text1:
        print("FAIL: turn 1 did not succeed", file=sys.stderr)
        return 1
    if not out1.get("memory") or not out1.get("memory_id_configured"):
        print("FAIL: Memory not enabled on Runtime (Story 3.2 prerequisite)", file=sys.stderr)
        return 1
    if not out1.get("gateway_tools"):
        print("FAIL: gateway_tools false — Gateway env missing", file=sys.stderr)
        return 1
    if not _HER2_CONTEXT.search(text1):
        print("FAIL: turn 1 missing Herceptin/HER2 context", file=sys.stderr)
        return 1
    if _CLINICAL_ORDER.search(text1):
        print("FAIL: turn 1 violated research-assist boundary", file=sys.stderr)
        return 1

    turn2 = _invoke(client, arn, session, TURN2)
    out2 = turn2.get("output") or {}
    text2 = _text(turn2)
    if turn2.get("status") != "success" or not text2:
        print("FAIL: turn 2 did not succeed", file=sys.stderr)
        return 1
    if not out2.get("memory"):
        print("FAIL: turn 2 did not use Memory path", file=sys.stderr)
        return 1
    if not _HER2_CONTEXT.search(text2):
        print(
            "FAIL: turn 2 lost Herceptin/HER2 context (FR17); "
            f"got {text2[:400]!r}",
            file=sys.stderr,
        )
        return 1
    # Cardiotoxicity / cardiac vulnerability framing expected in turn 2
    if not re.search(
        r"cardio|cardiac|heart|ejection|LVEF|CHF|heart failure",
        text2,
        flags=re.I,
    ):
        print("FAIL: turn 2 missing cardiotoxicity / cardiac risk framing", file=sys.stderr)
        return 1
    if _CLINICAL_ORDER.search(text2):
        print("FAIL: turn 2 violated research-assist boundary", file=sys.stderr)
        return 1

    ids1 = _source_ids(text1)
    ids2 = _source_ids(text2)
    combined = {
        "pmid": sorted(set(ids1["pmid"] + ids2["pmid"])),
        "nct": sorted(set(ids1["nct"] + ids2["nct"])),
        "chembl": sorted(set(ids1["chembl"] + ids2["chembl"])),
    }
    # FR11: when tools return IDs they should surface — soft check: at least one
    # identifier family across the two turns (Gateway pubmed path typically yields PMIDs).
    has_ids = bool(combined["pmid"] or combined["nct"] or combined["chembl"])
    if not has_ids:
        print(
            "WARN: no PMID/NCT/ChEMBL surfaced in either turn "
            "(acceptable only if tools returned empty ids)",
            file=sys.stderr,
        )

    summary = {
        "ok": True,
        "story": "3.3",
        "session": session,
        "memory": True,
        "gateway_tools": True,
        "turn1_chars": len(text1),
        "turn2_chars": len(text2),
        "her2_context_turn2": True,
        "research_assist_ok": True,
        "source_ids": combined,
        "source_ids_present": has_ids,
    }
    print(json.dumps(summary, indent=2))
    # Soft fail only if both turns discuss HER2 but tools clearly should have fired —
    # require at least one PMID across turns for a green smoke (Herceptin literature is dense).
    if not has_ids:
        print("FAIL: expected at least one source identifier (FR11)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
