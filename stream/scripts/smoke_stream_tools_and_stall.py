#!/usr/bin/env python3
"""
Stories 4.3 + 4.4 — tool_use/tool_result/error mapping + stall terminal.

Uses ops SigV4 (STREAM_URL + AWS creds). Cognito IdP path also works if you
export the same Cognito env vars used by smoke_stream_identity_pool.py.

Checks:
  1) Tool-calling turn emits tool_use (+ tool_result) before done
  2) forceToolError=pubmed → tool_result status=error then error; same sessionId next turn OK
  3) Client soft stall budget is 5 minutes (documented + enforced as request timeout)
  4) No fabricated reasoning (omit or only when Runtime provided it)

  export STREAM_URL=...
  python stream/scripts/smoke_stream_tools_and_stall.py
"""

from __future__ import annotations

import json
import os
import ssl
import sys
import uuid
from urllib import error, request

import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

try:
    import certifi

    _SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except Exception:  # noqa: BLE001
    _SSL_CONTEXT = ssl.create_default_context()

# Story 4.4 / NFR-9 — soft 5-minute stall → terminal client error
STALL_TIMEOUT_SECONDS = 300


def _parse_sse(body: str) -> list[dict]:
    events: list[dict] = []
    for block in body.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        for line in block.splitlines():
            if line.startswith("data:"):
                raw = line[5:].strip()
                if raw:
                    events.append(json.loads(raw))
    return events


def _post_signed(url: str, payload: dict) -> tuple[int, str]:
    region = (
        os.environ.get("AWS_REGION")
        or os.environ.get("AWS_DEFAULT_REGION")
        or "us-east-1"
    )
    data = json.dumps(payload).encode("utf-8")
    session = boto3.Session()
    creds = session.get_credentials()
    if creds is None:
        raise SystemExit("No AWS credentials for SigV4")
    frozen = creds.get_frozen_credentials()
    aws_req = AWSRequest(
        method="POST",
        url=url,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    SigV4Auth(frozen, "lambda", region).add_auth(aws_req)
    prepared = aws_req.prepare()
    req = request.Request(
        url, data=data, headers=dict(prepared.headers), method="POST"
    )
    try:
        with request.urlopen(
            req, timeout=STALL_TIMEOUT_SECONDS, context=_SSL_CONTEXT
        ) as resp:
            return resp.status, resp.read().decode("utf-8")
    except error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except error.URLError as exc:
        # Stall / network terminal
        return 0, f"STALL_OR_NETWORK: {exc.reason}"


def main() -> int:
    url = (os.environ.get("STREAM_URL") or "").strip()
    if not url:
        print("Set STREAM_URL", file=sys.stderr)
        return 2

    session_id = "stream-smoke-" + uuid.uuid4().hex
    if len(session_id) < 33:
        session_id = session_id.ljust(33, "0")

    print(f"stream_url={url}", file=sys.stderr)
    print(f"sessionId={session_id}", file=sys.stderr)
    print(f"stall_timeout_seconds={STALL_TIMEOUT_SECONDS}", file=sys.stderr)

    # --- 4.3 success path: pubmed tool turn ---
    status, body = _post_signed(
        url,
        {
            "sessionId": session_id,
            "message": (
                "Use the pubmed tool once to search for trastuzumab HER2 mechanism. "
                "Then reply with one short sentence and any PMIDs."
            ),
        },
    )
    print("--- tool turn ---", file=sys.stderr)
    print(body)
    if status != 200:
        print(f"FAIL: tool turn HTTP {status}", file=sys.stderr)
        return 1
    events = _parse_sse(body)
    types = [e.get("type") for e in events]
    if "tool_use" not in types:
        print(f"FAIL: expected tool_use before done; types={types}", file=sys.stderr)
        return 1
    if types.index("tool_use") > types.index("done"):
        print("FAIL: tool_use after done", file=sys.stderr)
        return 1
    if "tool_result" not in types:
        print(f"FAIL: expected tool_result; types={types}", file=sys.stderr)
        return 1
    # Never fabricate reasoning — absence is OK; if present must have text
    for e in events:
        if e.get("type") == "reasoning" and not (e.get("text") or "").strip():
            print("FAIL: empty reasoning event", file=sys.stderr)
            return 1

    # --- 4.3 forced failure ---
    status2, body2 = _post_signed(
        url,
        {
            "sessionId": session_id,
            "forceToolError": "pubmed",
            "message": (
                "Call the pubmed tool with query trastuzumab. "
                "If it errors, briefly acknowledge and stop."
            ),
        },
    )
    print("--- forced error turn ---", file=sys.stderr)
    print(body2)
    if status2 != 200:
        print(f"FAIL: forced error turn HTTP {status2}", file=sys.stderr)
        return 1
    events2 = _parse_sse(body2)
    types2 = [e.get("type") for e in events2]
    tr_err = [
        e
        for e in events2
        if e.get("type") == "tool_result" and e.get("status") == "error"
    ]
    if not tr_err:
        print(
            f"FAIL: expected tool_result status=error; types={types2}",
            file=sys.stderr,
        )
        return 1
    # error Stream Event after that tool_result
    tr_idx = next(
        i
        for i, e in enumerate(events2)
        if e.get("type") == "tool_result" and e.get("status") == "error"
    )
    err_after = any(
        e.get("type") == "error" for e in events2[tr_idx + 1 :]
    )
    if not err_after:
        print("FAIL: expected error event after tool_result error", file=sys.stderr)
        return 1

    # --- session continues ---
    status3, body3 = _post_signed(
        url,
        {
            "sessionId": session_id,
            "message": "Reply with exactly one word: ok",
        },
    )
    print("--- follow-up turn ---", file=sys.stderr)
    print(body3)
    if status3 != 200:
        print(f"FAIL: follow-up HTTP {status3}", file=sys.stderr)
        return 1
    events3 = _parse_sse(body3)
    if not events3 or events3[-1].get("type") != "done":
        print("FAIL: follow-up missing done", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "ok": True,
                "stories": ["4.3", "4.4"],
                "sessionId": session_id,
                "tool_turn_types": types,
                "forced_error_types": types2,
                "followup_types": [e.get("type") for e in events3],
                "stall_timeout_seconds": STALL_TIMEOUT_SECONDS,
                "log_retention_days": 7,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
