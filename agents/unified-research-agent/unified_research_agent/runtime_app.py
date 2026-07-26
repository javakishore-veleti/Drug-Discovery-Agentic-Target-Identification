"""
AgentCore Runtime HTTP contract (Stories 3.1–4.3).

Public service contract (AWS docs):
  POST /invocations  — agent turn
  GET  /ping         — health
  listen 0.0.0.0:8080

Returns answer text plus real tool_events / optional reasoning extracted from
Strands messages (never fabricated — AD-5). Supports forceToolError for Story 4.3.
"""

from __future__ import annotations

import asyncio
import logging
import traceback
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, Request

from .agent import create_agent
from .config import (
    get_agentcore_gateway_url,
    get_agentcore_memory_id,
    get_bedrock_model_id,
    use_gateway_tools,
)
from .memory_session import build_memory_session_manager, memory_enabled
from .tool_trace import extract_activity_from_messages, set_force_tool_error

logger = logging.getLogger("unified_research_agent.runtime")
logging.basicConfig(level=logging.INFO)

_SESSION_HEADER = "x-amzn-bedrock-agentcore-runtime-session-id"

app = FastAPI(
    title="Unified Research Agent",
    version="0.1.0",
    description="Agentic Target ID — single Strands agent for AgentCore Runtime",
)

def _extract_text(result: Any) -> str:
    if result is None:
        return ""
    if isinstance(result, str):
        return result
    message = getattr(result, "message", None)
    if isinstance(message, dict):
        content = message.get("content")
        if isinstance(content, list):
            parts: list[str] = []
            for block in content:
                if isinstance(block, dict) and block.get("text"):
                    parts.append(str(block["text"]))
                elif isinstance(block, str):
                    parts.append(block)
            if parts:
                return "\n".join(parts)
        if message.get("text"):
            return str(message["text"])
    return str(result)


def _prompt_from_body(body: Any) -> str:
    if body is None:
        return ""
    if isinstance(body, str):
        return body.strip()
    if not isinstance(body, dict):
        return str(body).strip()

    inner = body.get("input")
    if isinstance(inner, dict):
        for key in ("prompt", "query", "message", "text"):
            val = inner.get(key)
            if val is not None and str(val).strip():
                return str(val).strip()
    if isinstance(inner, str) and inner.strip():
        return inner.strip()

    for key in ("prompt", "query", "message", "text"):
        val = body.get(key)
        if val is not None and str(val).strip():
            return str(val).strip()
    return ""


def _session_id_from_request(request: Request, body: Any) -> str:
    header = (request.headers.get(_SESSION_HEADER) or "").strip()
    if header:
        return header
    if isinstance(body, dict):
        for key in ("session_id", "sessionId", "runtimeSessionId"):
            val = body.get(key)
            if val is not None and str(val).strip():
                return str(val).strip()
        inner = body.get("input")
        if isinstance(inner, dict):
            for key in ("session_id", "sessionId"):
                val = inner.get(key)
                if val is not None and str(val).strip():
                    return str(val).strip()
    return ""


def _force_tool_error_from_body(body: Any) -> str:
    if not isinstance(body, dict):
        return ""
    for key in ("forceToolError", "force_tool_error"):
        val = body.get(key)
        if val is not None and str(val).strip():
            return str(val).strip().lower()
    inner = body.get("input")
    if isinstance(inner, dict):
        for key in ("forceToolError", "force_tool_error"):
            val = inner.get(key)
            if val is not None and str(val).strip():
                return str(val).strip().lower()
    return ""


def _run_turn(
    prompt: str,
    session_id: str,
    *,
    force_tool_error: str = "",
) -> dict[str, Any]:
    set_force_tool_error(force_tool_error or None)
    try:
        if memory_enabled():
            if not session_id:
                raise ValueError(
                    "session_id required when AGENTCORE_MEMORY_ID is set "
                    "(Runtime Session-Id header or body.session_id)"
                )
            with build_memory_session_manager(session_id) as session_manager:
                agent = create_agent(session_manager=session_manager)
                start = len(getattr(agent, "messages", []) or [])
                result = agent(prompt)
                tool_events, reasoning = extract_activity_from_messages(
                    list(getattr(agent, "messages", []) or []),
                    start_index=start,
                )
                return {
                    "text": _extract_text(result),
                    "used_memory": True,
                    "tool_events": tool_events,
                    "reasoning": reasoning,
                }

        agent = create_agent()
        result = agent(prompt)
        tool_events, reasoning = extract_activity_from_messages(
            list(getattr(agent, "messages", []) or []),
            start_index=0,
        )
        return {
            "text": _extract_text(result),
            "used_memory": False,
            "tool_events": tool_events,
            "reasoning": reasoning,
        }
    finally:
        set_force_tool_error(None)


@app.get("/ping")
def ping() -> dict[str, str]:
    return {"status": "Healthy"}


@app.post("/invocations")
async def invoke_agent(request: Request) -> dict[str, Any]:
    try:
        body = await request.json()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail="Request body must be JSON") from exc

    prompt = _prompt_from_body(body)
    if not prompt:
        raise HTTPException(
            status_code=400,
            detail="No prompt found. Provide input.prompt (or top-level prompt).",
        )

    session_id = _session_id_from_request(request, body)
    force_tool_error = _force_tool_error_from_body(body)

    try:
        turn = await asyncio.to_thread(
            _run_turn,
            prompt,
            session_id,
            force_tool_error=force_tool_error,
        )
        text = turn["text"]
        tool_events = turn["tool_events"]
        reasoning = turn["reasoning"]
        return {
            "response": text,
            "status": "success",
            "output": {
                "message": text,
                "model_id": get_bedrock_model_id(),
                "gateway_tools": use_gateway_tools()
                and bool(get_agentcore_gateway_url()),
                "memory": turn["used_memory"],
                "memory_id_configured": bool(get_agentcore_memory_id()),
                "session_id": session_id or None,
                "tool_events": tool_events,
                # Only non-empty when Strands emitted reasoningContent (AD-5).
                "reasoning": reasoning,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.error(
            "Agent processing failed: %s: %s\n%s",
            exc.__class__.__name__,
            exc,
            traceback.format_exc(),
        )
        msg = str(exc).strip().replace("\n", " ")[:240]
        raise HTTPException(
            status_code=500,
            detail=f"Agent processing failed: {exc.__class__.__name__}: {msg}",
        ) from exc
