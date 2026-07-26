"""
AgentCore Runtime HTTP contract (Story 3.1).

Public service contract (AWS docs):
  POST /invocations  — agent turn
  GET  /ping         — health
  listen 0.0.0.0:8080

Single Unified Research Agent entrypoint (AD-2) — no multi-agent swarm.
"""

from __future__ import annotations

import logging
import traceback
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, Request

from .agent import create_agent
from .config import (
    get_agentcore_gateway_url,
    get_bedrock_model_id,
    use_gateway_tools,
)

logger = logging.getLogger("unified_research_agent.runtime")
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Unified Research Agent",
    version="0.1.0",
    description="Agentic Target ID — single Strands agent for AgentCore Runtime",
)

# One agent instance per container process (AD-2).
_agent = create_agent()


def _extract_text(result: Any) -> str:
    """Best-effort string from a Strands AgentResult / message."""
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
    """
    Accept common AgentCore / docs shapes:
      {"input": {"prompt": "..."}}
      {"prompt": "..."}
      {"input": "..."}
      "..."
    """
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


@app.get("/ping")
def ping() -> dict[str, str]:
    # AgentCore HTTP contract: Healthy | HealthyBusy (not lowercase "healthy").
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

    try:
        result = _agent(prompt)
        text = _extract_text(result)
        # Contract-shaped fields + diagnostics for smoke (Story 3.1).
        return {
            "response": text,
            "status": "success",
            "output": {
                "message": text,
                "model_id": get_bedrock_model_id(),
                "gateway_tools": use_gateway_tools()
                and bool(get_agentcore_gateway_url()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001 — Runtime boundary
        logger.error(
            "Agent processing failed: %s: %s\n%s",
            exc.__class__.__name__,
            exc,
            traceback.format_exc(),
        )
        # Surface a short, non-secret message for smoke/debug (no stack in body).
        msg = str(exc).strip().replace("\n", " ")[:240]
        raise HTTPException(
            status_code=500,
            detail=f"Agent processing failed: {exc.__class__.__name__}: {msg}",
        ) from exc
