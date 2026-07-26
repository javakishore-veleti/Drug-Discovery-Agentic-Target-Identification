#!/usr/bin/env python3
"""Invoke AgentCore Runtime (Story 3.1 smoke). Requires AGENT_RUNTIME_ARN."""

from __future__ import annotations

import json
import os
import sys
import uuid

import boto3


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
    prompt = " ".join(sys.argv[1:]).strip() or "Reply with exactly one word: ok"
    session = ("smoke-" + uuid.uuid4().hex)
    if len(session) < 33:
        session = session.ljust(33, "0")

    client = boto3.client("bedrock-agentcore", region_name=region)
    payload = json.dumps({"input": {"prompt": prompt}})
    print(f"runtime={arn}", file=sys.stderr)
    print(f"session={session}", file=sys.stderr)
    print(f"model_env_hint=BEDROCK_MODEL_ID pinned on Runtime", file=sys.stderr)

    resp = client.invoke_agent_runtime(
        agentRuntimeArn=arn,
        runtimeSessionId=session,
        payload=payload,
        qualifier="DEFAULT",
    )
    body = resp["response"].read()
    print(body.decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
