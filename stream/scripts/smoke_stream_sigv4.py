#!/usr/bin/env python3
"""
Story 4.1 — SigV4 smoke client for the Stream Function URL.

Uses the caller's AWS credentials (CLI profile / env). Does NOT use AgentCore
Runtime IAM and does not call Runtime directly (AD-1 / FR8).

  export STREAM_URL=https://....lambda-url.us-east-1.on.aws/
  python stream/scripts/smoke_stream_sigv4.py "Reply with exactly one word: ok"
"""

from __future__ import annotations

import json
import os
import ssl
import sys
from urllib import error, request

import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

try:
    import certifi

    _SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except Exception:  # noqa: BLE001
    _SSL_CONTEXT = ssl.create_default_context()


def _parse_sse(body: str) -> list[dict]:
    events: list[dict] = []
    for block in body.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        for line in block.splitlines():
            if line.startswith("data:"):
                raw = line[5:].strip()
                if not raw:
                    continue
                events.append(json.loads(raw))
    return events


def main() -> int:
    url = (os.environ.get("STREAM_URL") or "").strip()
    if not url:
        print("Set STREAM_URL to the CDK StreamUrl output", file=sys.stderr)
        return 2
    region = (
        os.environ.get("AWS_REGION")
        or os.environ.get("AWS_DEFAULT_REGION")
        or "us-east-1"
    )
    message = " ".join(sys.argv[1:]).strip() or "Reply with exactly one word: ok"
    session_id = (os.environ.get("SESSION_ID") or "").strip() or None

    payload: dict = {"message": message}
    if session_id:
        payload["sessionId"] = session_id

    session = boto3.Session()
    creds = session.get_credentials()
    if creds is None:
        print("No AWS credentials found for SigV4", file=sys.stderr)
        return 2
    frozen = creds.get_frozen_credentials()

    data = json.dumps(payload).encode("utf-8")
    aws_req = AWSRequest(
        method="POST",
        url=url,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    SigV4Auth(frozen, "lambda", region).add_auth(aws_req)
    prepared = aws_req.prepare()

    print(f"stream_url={url}", file=sys.stderr)
    print("auth=SigV4 Function URL (not AgentCore Runtime)", file=sys.stderr)

    req = request.Request(
        url,
        data=data,
        headers=dict(prepared.headers),
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=300, context=_SSL_CONTEXT) as resp:
            body = resp.read().decode("utf-8")
            status = resp.status
    except error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        print(f"HTTP {exc.code}: {err_body}", file=sys.stderr)
        return 1

    print(body)
    events = _parse_sse(body)
    types = [e.get("type") for e in events]
    print(f"http_status={status} event_types={types}", file=sys.stderr)

    if not events or events[0].get("type") != "session_started":
        print("FAIL: first event must be session_started", file=sys.stderr)
        return 1
    if not events[0].get("sessionId"):
        print("FAIL: session_started missing sessionId", file=sys.stderr)
        return 1
    if events[-1].get("type") != "done":
        print("FAIL: last event must be done", file=sys.stderr)
        return 1
    if "token" not in types and "error" not in types:
        print("FAIL: expected token or error before done", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "ok": True,
                "sessionId": events[0].get("sessionId"),
                "types": types,
                "token_chars": sum(
                    len(e.get("text") or "") for e in events if e.get("type") == "token"
                ),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
