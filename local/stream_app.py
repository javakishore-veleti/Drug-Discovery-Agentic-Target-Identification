"""
Local Stream equivalent — no Cognito, no SigV4, no AgentCore Runtime.

Feature toggle target for VITE_STACK_MODE=local:
  Browser → POST http://127.0.0.1:8787/ → in-process agent (unified or specialist)
  Tools: local adapters (Gateway MCP forced off).

Same SSE event shapes as stream/handler.py (session_started, tool_*, token, error, done).
"""

from __future__ import annotations

import json
import logging
import os
import sys
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse

_REPO = Path(__file__).resolve().parents[1]
_URA = _REPO / "agents" / "unified-research-agent"
_AGENTS = _REPO / "agents"
for path in (_AGENTS, _URA, _REPO):
    p = str(path)
    if path.is_dir() and p not in sys.path:
        sys.path.insert(0, p)

from dotenv import load_dotenv

load_dotenv(_URA / ".env", override=False)
load_dotenv(_REPO / "local" / ".env", override=False)

# Local Stream never uses AgentCore Gateway (cost / destroyed stacks).
os.environ["USE_GATEWAY_TOOLS"] = "false"
os.environ.pop("AGENTCORE_GATEWAY_URL", None)

from local.agent_registry import (  # noqa: E402
    DEFAULT_AGENT_ID,
    create_agent_by_id,
    list_agents,
    normalize_agent_id,
)
from local.bedrock_trace import TRACE, render_trace_html  # noqa: E402
from local.traced_bedrock import TracedBedrockModel, wrap_agent_model  # noqa: E402
from local.turn_debug import build_turn_debug, persist_turn_debug  # noqa: E402
from unified_research_agent.config import (  # noqa: E402
    get_aws_region,
    get_bedrock_model_id,
)
from unified_research_agent.tool_trace import extract_activity_from_messages  # noqa: E402

logger = logging.getLogger("local.stream")
logging.basicConfig(level=logging.INFO)

_TOKEN_CHUNK = 120
# session_id -> {"agent_id": str, "agent": Agent}
_sessions: dict[str, dict[str, Any]] = {}

app = FastAPI(title="Agentic Target ID — Local Stream", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS", "GET"],
    allow_headers=["*"],
)


def _mint_session_id() -> str:
    sid = "local-" + uuid.uuid4().hex
    return sid if len(sid) >= 33 else sid.ljust(33, "0")


def _sse(event: dict[str, Any]) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


def _chunk_tokens(text: str, size: int = _TOKEN_CHUNK) -> list[str]:
    if not text:
        return []
    return [text[i : i + size] for i in range(0, len(text), size)]


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


def _agent_for(session_id: str, agent_id: str) -> Any:
    entry = _sessions.get(session_id)
    if entry is None or entry.get("agent_id") != agent_id:
        _sessions[session_id] = {
            "agent_id": agent_id,
            "agent": create_agent_by_id(agent_id),
        }
    agent = _sessions[session_id]["agent"]
    if not isinstance(getattr(agent, "model", None), TracedBedrockModel):
        wrap_agent_model(agent, region_name=get_aws_region())
    return agent


def _build_sse(
    session_id: str,
    message: str,
    request_id: str,
    agent_id: str,
) -> str:
    parts: list[str] = [
        _sse(
            {
                "type": "session_started",
                "sessionId": session_id,
                "requestId": request_id,
                "mode": "local",
                "agentId": agent_id,
            }
        )
    ]
    if not message.strip():
        parts.append(
            _sse(
                {
                    "type": "error",
                    "message": "message is required",
                    "code": "bad_request",
                    "sessionId": session_id,
                    "agentId": agent_id,
                }
            )
        )
        parts.append(
            _sse({"type": "done", "sessionId": session_id, "agentId": agent_id})
        )
        return "".join(parts)

    try:
        agent = _agent_for(session_id, agent_id)
        TRACE.begin_turn(
            request_id=request_id,
            session_id=session_id,
            agent_id=agent_id,
            model_id=get_bedrock_model_id(),
            user_message=message,
        )
        start = len(getattr(agent, "messages", []) or [])
        result = agent(message)
        tool_events, reasoning = extract_activity_from_messages(
            list(getattr(agent, "messages", []) or []),
            start_index=start,
        )
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
                            "agentId": agent_id,
                        }
                    )
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
                    "agentId": agent_id,
                }
                if ev.get("summary"):
                    result_event["summary"] = ev.get("summary")
                if status == "error" and ev.get("message"):
                    result_event["message"] = ev.get("message")
                parts.append(_sse(result_event))
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
                                "agentId": agent_id,
                            }
                        )
                    )
        for text in reasoning:
            if text.strip():
                parts.append(
                    _sse(
                        {
                            "type": "reasoning",
                            "text": text,
                            "agentId": agent_id,
                        }
                    )
                )
        answer = _extract_text(result)
        for chunk in _chunk_tokens(answer):
            parts.append(
                _sse({"type": "token", "text": chunk, "agentId": agent_id})
            )

        debug = build_turn_debug(
            agent_id=agent_id,
            user_message=message,
            messages=list(getattr(agent, "messages", []) or []),
            start_index=start,
            request_id=request_id,
            session_id=session_id,
        )
        bedrock_trace = TRACE.end_turn()
        debug["bedrockCallCount"] = bedrock_trace.get("bedrockCallCount")
        debug["bedrockModelId"] = bedrock_trace.get("modelId")
        debug["bedrockTraceUrl"] = "http://127.0.0.1:8787/bedrock-trace"
        debug_path = persist_turn_debug(debug)
        if debug_path:
            debug["savedTo"] = debug_path
        logger.info(
            "turn_debug agent_id=%s bedrock_calls=%s tools_requested=%s tools_executed_host=%s",
            agent_id,
            debug.get("bedrockCallCount"),
            debug.get("toolsRequestedByBedrock"),
            debug.get("toolsExecutedOnHost"),
        )
        parts.append(
            _sse(
                {
                    "type": "debug",
                    "sessionId": session_id,
                    "agentId": agent_id,
                    "requestId": request_id,
                    "debug": debug,
                }
            )
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("local_stream_turn_failed agent_id=%s", agent_id)
        try:
            TRACE.end_turn()
        except Exception:  # noqa: BLE001
            pass
        parts.append(
            _sse(
                {
                    "type": "error",
                    "message": f"Local agent turn failed: {exc.__class__.__name__}: {exc}",
                    "code": "local_agent_error",
                    "sessionId": session_id,
                    "agentId": agent_id,
                }
            )
        )
    finally:
        parts.append(
            _sse({"type": "done", "sessionId": session_id, "agentId": agent_id})
        )
    return "".join(parts)


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "mode": "local",
        "defaultAgentId": DEFAULT_AGENT_ID,
        "agents": list_agents(),
    }


@app.get("/agents")
def agents() -> dict[str, Any]:
    return {"defaultAgentId": DEFAULT_AGENT_ID, "agents": list_agents()}


@app.get("/bedrock-trace", response_class=HTMLResponse)
def bedrock_trace_html() -> HTMLResponse:
    """Latest-turn Bedrock call viewer (auto-refresh HTML; no history)."""
    return HTMLResponse(
        content=render_trace_html(),
        headers={"Cache-Control": "no-store"},
    )


@app.get("/bedrock-trace.json")
def bedrock_trace_json() -> dict[str, Any]:
    return TRACE.as_dict()


@app.post("/")
async def stream_turn(request: Request) -> PlainTextResponse:
    request_id = str(uuid.uuid4())
    try:
        body = await request.json()
    except Exception:  # noqa: BLE001
        return PlainTextResponse(
            content=json.dumps({"error": "body must be JSON"}),
            status_code=400,
            media_type="application/json",
        )
    if not isinstance(body, dict):
        body = {}
    message = str(
        body.get("message") or body.get("prompt") or body.get("query") or ""
    ).strip()
    session_id = str(body.get("sessionId") or body.get("session_id") or "").strip()
    if not session_id:
        session_id = _mint_session_id()

    agent_id = normalize_agent_id(
        str(body.get("agentId") or body.get("agent_id") or "")
    )

    # If client reused a session under a different agent, start a fresh session.
    existing = _sessions.get(session_id)
    if existing is not None and existing.get("agent_id") != agent_id:
        session_id = _mint_session_id()

    sse = _build_sse(session_id, message, request_id, agent_id)
    return PlainTextResponse(
        content=sse,
        status_code=200,
        media_type="text/event-stream; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "X-Content-Type-Options": "nosniff",
            "X-Agent-Id": agent_id,
        },
    )
