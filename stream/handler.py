"""
Stream Lambda — SSE bridge to AgentCore Runtime (Stories 4.1–4.4).

Maps Runtime tool_events → tool_use / tool_result / error (AD-8).
Never fabricates reasoning (AD-5). Structured logs include sessionId, requestId,
and tool when applicable (Story 4.4). Soft stall budget aligns with 5-minute
Lambda timeout (NFR-9).
"""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Soft stall budget (NFR-9 / Story 4.4): Lambda timeout is 5 minutes in CDK.
_STALL_SECONDS = 300
_TOKEN_CHUNK = 120


def _env(name: str, default: str = "") -> str:
    return (os.environ.get(name) or default).strip()


def _log(msg: str, **fields: Any) -> None:
    payload = {"msg": msg, **{k: v for k, v in fields.items() if v is not None}}
    logger.info(json.dumps(payload, default=str))


def _emf_turn(
    *,
    function_name: str,
    duration_ms: float,
    tool_use_count: int,
    tool_error_count: int,
    turn_error: int,
) -> None:
    """
    Embedded Metric Format for Story M2.2 (namespace AgenticTargetId/Stream).

    Surfaces TurnDurationMs / ToolUseCount / ToolErrors / TurnErrors in CloudWatch
    without a custom metrics SDK dependency.
    """
    payload = {
        "_aws": {
            "Timestamp": int(time.time() * 1000),
            "CloudWatchMetrics": [
                {
                    "Namespace": "AgenticTargetId/Stream",
                    "Dimensions": [["FunctionName"]],
                    "Metrics": [
                        {"Name": "TurnDurationMs", "Unit": "Milliseconds"},
                        {"Name": "ToolUseCount", "Unit": "Count"},
                        {"Name": "ToolErrors", "Unit": "Count"},
                        {"Name": "TurnErrors", "Unit": "Count"},
                    ],
                }
            ],
        },
        "FunctionName": function_name or "agentic-target-id-stream",
        "TurnDurationMs": round(duration_ms, 2),
        "ToolUseCount": int(tool_use_count),
        "ToolErrors": int(tool_error_count),
        "TurnErrors": int(turn_error),
    }
    print(json.dumps(payload))


def _mint_session_id() -> str:
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


def _force_tool_error_from_body(body: dict[str, Any]) -> str:
    for key in ("forceToolError", "force_tool_error"):
        val = body.get(key)
        if val is not None and str(val).strip():
            return str(val).strip().lower()
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


def _tool_events_from_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    out = payload.get("output") if isinstance(payload, dict) else None
    if isinstance(out, dict) and isinstance(out.get("tool_events"), list):
        return [e for e in out["tool_events"] if isinstance(e, dict)]
    if isinstance(payload.get("tool_events"), list):
        return [e for e in payload["tool_events"] if isinstance(e, dict)]
    return []


def _reasoning_from_payload(payload: dict[str, Any]) -> list[str]:
    """Only pass through reasoning the Runtime actually exposed (AD-5)."""
    out = payload.get("output") if isinstance(payload, dict) else None
    raw = None
    if isinstance(out, dict):
        raw = out.get("reasoning")
    if raw is None:
        raw = payload.get("reasoning")
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]
    if isinstance(raw, str) and raw.strip():
        return [raw.strip()]
    return []


def _invoke_runtime(
    session_id: str,
    prompt: str,
    *,
    force_tool_error: str = "",
) -> dict[str, Any]:
    arn = _env("AGENT_RUNTIME_ARN")
    if not arn:
        raise RuntimeError("AGENT_RUNTIME_ARN is not configured on Stream Lambda")
    region = _env("AWS_REGION") or _env("AWS_DEFAULT_REGION") or "us-east-1"
    client = boto3.client("bedrock-agentcore", region_name=region)
    body: dict[str, Any] = {"input": {"prompt": prompt}}
    if force_tool_error:
        body["forceToolError"] = force_tool_error
        body["input"]["forceToolError"] = force_tool_error
    resp = client.invoke_agent_runtime(
        agentRuntimeArn=arn,
        runtimeSessionId=session_id,
        payload=json.dumps(body),
        qualifier="DEFAULT",
        contentType="application/json",
        accept="application/json",
    )
    raw = resp["response"].read()
    text = raw.decode("utf-8") if isinstance(raw, bytes) else str(raw)
    return json.loads(text) if text.strip() else {}


def _append_tool_stream_events(
    parts: list[str],
    tool_events: list[dict[str, Any]],
    *,
    session_id: str,
    request_id: str,
) -> None:
    """Emit tool_use / tool_result; on error status emit error (AD-8)."""
    for ev in tool_events:
        etype = ev.get("type")
        tool = ev.get("tool")
        if etype == "tool_use":
            parts.append(
                _sse(
                    {
                        "type": "tool_use",
                        "tool": tool,
                        "input": ev.get("input"),
                        "sessionId": session_id,
                    }
                )
            )
            _log(
                "stream_tool_use",
                sessionId=session_id,
                requestId=request_id,
                tool=tool,
            )
        elif etype == "tool_result":
            status = ev.get("status") or "ok"
            result_event = {
                "type": "tool_result",
                "tool": tool,
                "status": status,
                "ids": ev.get("ids")
                or {"pmid": [], "nct": [], "chembl": []},
                "sessionId": session_id,
            }
            if ev.get("summary"):
                result_event["summary"] = ev.get("summary")
            if status == "error" and ev.get("message"):
                result_event["message"] = ev.get("message")
            parts.append(_sse(result_event))
            _log(
                "stream_tool_result",
                sessionId=session_id,
                requestId=request_id,
                tool=tool,
                status=status,
            )
            if status == "error":
                parts.append(
                    _sse(
                        {
                            "type": "error",
                            "message": ev.get("message")
                            or f"Tool {tool} failed",
                            "code": "tool_error",
                            "tool": tool,
                            "sessionId": session_id,
                        }
                    )
                )
                _log(
                    "stream_tool_error_event",
                    sessionId=session_id,
                    requestId=request_id,
                    tool=tool,
                )


def _build_sse_turn(
    *,
    session_id: str,
    message: str,
    request_id: str,
    force_tool_error: str = "",
    function_name: str = "",
) -> tuple[str, int]:
    started = time.monotonic()
    turn_error = 0
    tool_use_count = 0
    tool_error_count = 0
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
        _emf_turn(
            function_name=function_name,
            duration_ms=(time.monotonic() - started) * 1000,
            tool_use_count=0,
            tool_error_count=0,
            turn_error=1,
        )
        return "".join(parts), 400

    try:
        _log(
            "runtime_invoke_start",
            sessionId=session_id,
            requestId=request_id,
            forceToolError=force_tool_error or None,
            stallBudgetSeconds=_STALL_SECONDS,
        )
        payload = _invoke_runtime(
            session_id,
            message,
            force_tool_error=force_tool_error,
        )
        tool_events = _tool_events_from_payload(payload)
        tool_use_count = sum(1 for e in tool_events if e.get("type") == "tool_use")
        tool_error_count = sum(
            1
            for e in tool_events
            if e.get("type") == "tool_result" and e.get("status") == "error"
        )
        _append_tool_stream_events(
            parts,
            tool_events,
            session_id=session_id,
            request_id=request_id,
        )

        # AD-5: only if Runtime exposed reasoningContent — never invent from tokens.
        for text in _reasoning_from_payload(payload):
            parts.append(_sse({"type": "reasoning", "text": text}))

        answer = _extract_runtime_text(payload)
        for chunk in _chunk_tokens(answer):
            parts.append(_sse({"type": "token", "text": chunk}))

        _log(
            "runtime_invoke_ok",
            sessionId=session_id,
            requestId=request_id,
            chars=len(answer),
            toolCount=tool_use_count,
        )
    except (ClientError, BotoCoreError, json.JSONDecodeError, RuntimeError, ValueError) as exc:
        turn_error = 1
        _log(
            "runtime_invoke_failed",
            sessionId=session_id,
            requestId=request_id,
            error=exc.__class__.__name__,
        )
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
                    "sessionId": session_id,
                }
            )
        )
    finally:
        parts.append(_sse({"type": "done", "sessionId": session_id}))
        _log("stream_done", sessionId=session_id, requestId=request_id)
        _emf_turn(
            function_name=function_name,
            duration_ms=(time.monotonic() - started) * 1000,
            tool_use_count=tool_use_count,
            tool_error_count=tool_error_count,
            turn_error=turn_error,
        )

    return "".join(parts), 200


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    request_id = getattr(context, "aws_request_id", None) or str(uuid.uuid4())
    method = (
        (event.get("requestContext") or {}).get("http", {}).get("method")
        or event.get("httpMethod")
        or "POST"
    ).upper()

    # CORS is owned by the Function URL config (CDK). Do not also emit
    # Access-Control-* here — browsers reject duplicated Allow-Origin values.

    if method == "OPTIONS":
        return {"statusCode": 204, "headers": {}, "body": ""}

    if method != "POST":
        return {
            "statusCode": 405,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "POST required"}),
        }

    try:
        body = _parse_body(event)
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "body must be JSON"}),
        }

    session_id = _session_from_body(body) or _mint_session_id()
    message = _message_from_body(body)
    force_tool_error = _force_tool_error_from_body(body)
    function_name = getattr(context, "function_name", None) or _env(
        "AWS_LAMBDA_FUNCTION_NAME", "agentic-target-id-stream"
    )
    _log(
        "stream_request",
        sessionId=session_id,
        requestId=request_id,
        tool=force_tool_error or None,
    )

    sse_body, status = _build_sse_turn(
        session_id=session_id,
        message=message,
        request_id=request_id,
        force_tool_error=force_tool_error,
        function_name=function_name,
    )

    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "text/event-stream; charset=utf-8",
            "Cache-Control": "no-cache",
            "X-Content-Type-Options": "nosniff",
        },
        "body": sse_body,
    }
