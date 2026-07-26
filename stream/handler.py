"""
Stream Lambda — SSE bridge to AgentCore Runtime (Story 4.1 / AD-4 / AD-7).

Clients call this Function URL (SigV4 / IAM). They never invoke AgentCore Runtime
directly and never hold Runtime IAM credentials (AD-1 / FR8).

V1: Runtime returns a completed JSON turn; we map it into ordered SSE events and
emit ``done`` only after that invoke finishes (or hard-aborts).
``reasoning`` / ``tool_use`` / ``tool_result`` are reserved for Story 4.3 when
Runtime exposes them — never fabricated (AD-5).
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Soft stall budget alignment (NFR-9): keep Lambda timeout ≤ 5 minutes in CDK.
_TOKEN_CHUNK = 120


def _env(name: str, default: str = "") -> str:
    return (os.environ.get(name) or default).strip()


def _mint_session_id() -> str:
    """Stream-owned Chat Session id (AD-7). Runtime requires ≥ 33 chars."""
    sid = "stream-" + uuid.uuid4().hex
    return sid if len(sid) >= 33 else sid.ljust(33, "0")


def _parse_body(event: dict[str, Any]) -> dict[str, Any]:
    raw = event.get("body")
    if raw is None:
        return {}
    if event.get("isBase64Encoded"):
        import base64

        raw = base64.b64decode(raw).decode("utf-8")
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8")
    if isinstance(raw, str):
        raw = raw.strip()
        if not raw:
            return {}
        return json.loads(raw)
    if isinstance(raw, dict):
        return raw
    return {}


def _message_from_body(body: dict[str, Any]) -> str:
    for key in ("message", "prompt", "query", "text"):
        val = body.get(key)
        if val is not None and str(val).strip():
            return str(val).strip()
    inner = body.get("input")
    if isinstance(inner, dict):
        for key in ("message", "prompt", "query", "text"):
            val = inner.get(key)
            if val is not None and str(val).strip():
                return str(val).strip()
    if isinstance(inner, str) and inner.strip():
        return inner.strip()
    return ""


def _session_from_body(body: dict[str, Any]) -> str:
    for key in ("sessionId", "session_id"):
        val = body.get(key)
        if val is not None and str(val).strip():
            return str(val).strip()
    return ""


def _sse(event: dict[str, Any]) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


def _chunk_tokens(text: str, size: int = _TOKEN_CHUNK) -> list[str]:
    if not text:
        return []
    return [text[i : i + size] for i in range(0, len(text), size)]


def _extract_runtime_text(payload: dict[str, Any]) -> str:
    if not isinstance(payload, dict):
        return str(payload)
    if payload.get("response"):
        return str(payload["response"])
    out = payload.get("output")
    if isinstance(out, dict) and out.get("message") is not None:
        return str(out["message"])
    if isinstance(out, str):
        return out
    return json.dumps(payload)


def _invoke_runtime(session_id: str, prompt: str) -> dict[str, Any]:
    arn = _env("AGENT_RUNTIME_ARN")
    if not arn:
        raise RuntimeError("AGENT_RUNTIME_ARN is not configured on Stream Lambda")
    region = _env("AWS_REGION") or _env("AWS_DEFAULT_REGION") or "us-east-1"
    client = boto3.client("bedrock-agentcore", region_name=region)
    resp = client.invoke_agent_runtime(
        agentRuntimeArn=arn,
        runtimeSessionId=session_id,
        payload=json.dumps({"input": {"prompt": prompt}}),
        qualifier="DEFAULT",
        contentType="application/json",
        accept="application/json",
    )
    raw = resp["response"].read()
    if isinstance(raw, bytes):
        text = raw.decode("utf-8")
    else:
        text = str(raw)
    return json.loads(text) if text.strip() else {}


def _build_sse_turn(
    *,
    session_id: str,
    message: str,
    request_id: str,
) -> tuple[str, int]:
    """
    Build full SSE body for one turn.

    Always ends with ``done`` after Runtime returns or a hard abort (AD-4).
    """
    parts: list[str] = [
        _sse(
            {
                "type": "session_started",
                "sessionId": session_id,
                "requestId": request_id,
            }
        )
    ]

    if not message:
        parts.append(
            _sse(
                {
                    "type": "error",
                    "message": "message is required",
                    "code": "bad_request",
                }
            )
        )
        parts.append(_sse({"type": "done", "sessionId": session_id}))
        return "".join(parts), 400

    try:
        logger.info(
            json.dumps(
                {
                    "msg": "runtime_invoke_start",
                    "sessionId": session_id,
                    "requestId": request_id,
                }
            )
        )
        payload = _invoke_runtime(session_id, message)
        text = _extract_runtime_text(payload)
        for chunk in _chunk_tokens(text):
            parts.append(_sse({"type": "token", "text": chunk}))
        logger.info(
            json.dumps(
                {
                    "msg": "runtime_invoke_ok",
                    "sessionId": session_id,
                    "requestId": request_id,
                    "chars": len(text),
                }
            )
        )
    except (ClientError, BotoCoreError, json.JSONDecodeError, RuntimeError, ValueError) as exc:
        logger.exception(
            "runtime_invoke_failed sessionId=%s requestId=%s",
            session_id,
            request_id,
        )
        parts.append(
            _sse(
                {
                    "type": "error",
                    "message": f"Runtime turn failed: {exc.__class__.__name__}",
                    "code": "runtime_error",
                }
            )
        )
    finally:
        # AD-4: done only after Runtime turn closes (or hard abort path above).
        parts.append(_sse({"type": "done", "sessionId": session_id}))

    return "".join(parts), 200


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    request_id = getattr(context, "aws_request_id", None) or str(uuid.uuid4())
    method = (
        (event.get("requestContext") or {}).get("http", {}).get("method")
        or event.get("httpMethod")
        or "POST"
    ).upper()

    if method == "OPTIONS":
        return {
            "statusCode": 204,
            "headers": _cors_headers(),
            "body": "",
        }

    if method != "POST":
        return {
            "statusCode": 405,
            "headers": {**_cors_headers(), "Content-Type": "application/json"},
            "body": json.dumps({"error": "POST required"}),
        }

    try:
        body = _parse_body(event)
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": {**_cors_headers(), "Content-Type": "application/json"},
            "body": json.dumps({"error": "body must be JSON"}),
        }

    session_id = _session_from_body(body) or _mint_session_id()
    message = _message_from_body(body)
    sse_body, status = _build_sse_turn(
        session_id=session_id,
        message=message,
        request_id=request_id,
    )

    return {
        "statusCode": status,
        "headers": {
            **_cors_headers(),
            "Content-Type": "text/event-stream; charset=utf-8",
            "Cache-Control": "no-cache",
            "X-Content-Type-Options": "nosniff",
        },
        "body": sse_body,
    }


def _cors_headers() -> dict[str, str]:
    # Browser CORS is finalized with Cognito UI; allow common smoke headers now.
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "authorization,content-type,x-amz-date,x-amz-security-token",
        "Access-Control-Allow-Methods": "POST,OPTIONS",
    }
