#!/usr/bin/env python3
"""
Story 3.2 — two-turn Runtime smoke with the same session key.

Turn 1 sets a research focus compound; turn 2 asks for it without restating.
Requires AGENT_RUNTIME_ARN (Gateway + Memory wired on Runtime).
"""

from __future__ import annotations

import json
import os
import re
import sys
import uuid

import boto3

FOCUS = "trastuzumab"


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
    session = "smoke-mem-" + uuid.uuid4().hex
    if len(session) < 33:
        session = session.ljust(33, "0")

    client = boto3.client("bedrock-agentcore", region_name=region)
    print(f"runtime={arn}", file=sys.stderr)
    print(f"session={session}", file=sys.stderr)
    print(f"focus={FOCUS}", file=sys.stderr)

    turn1 = _invoke(
        client,
        arn,
        session,
        f"For this Chat Session, our research focus compound is {FOCUS}. "
        "Confirm the focus compound name in one short sentence. "
        "Do not call tools.",
    )
    out1 = turn1.get("output") or {}
    if not out1.get("memory") or not out1.get("memory_id_configured"):
        print("FAIL: Runtime did not enable Memory for turn 1", file=sys.stderr)
        return 1
    text1 = (turn1.get("response") or "").lower()
    if FOCUS not in text1 and "herceptin" not in text1:
        print(
            f"FAIL: turn 1 did not acknowledge focus {FOCUS!r}; got {text1!r}",
            file=sys.stderr,
        )
        return 1

    turn2 = _invoke(
        client,
        arn,
        session,
        "What is our research focus compound in this session? "
        "Reply with the compound name only. Do not call tools.",
    )
    out2 = turn2.get("output") or {}
    if not out2.get("memory"):
        print("FAIL: turn 2 did not use Memory path", file=sys.stderr)
        return 1
    text2 = (turn2.get("response") or turn2.get("output", {}).get("message") or "").strip()
    if not re.search(r"trastuzumab|herceptin", text2, flags=re.I):
        print(
            f"FAIL: turn 2 did not retain focus compound; got {text2!r}",
            file=sys.stderr,
        )
        return 1

    print(
        json.dumps(
            {
                "ok": True,
                "session": session,
                "focus": FOCUS,
                "turn2": text2,
                "memory": out2.get("memory"),
                "memory_id_configured": out2.get("memory_id_configured"),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
