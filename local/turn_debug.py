"""
Serialize one local agent turn for UI/debug (what Bedrock saw vs tool execution).

Bedrock never runs tools; tools run in this host process. Proof of execution is
toolResult blocks in Strands messages + adapter status/ids.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
_TURN_DIR = _REPO / ".local-run" / "turns"


def _as_dict(msg: Any) -> dict[str, Any]:
    if isinstance(msg, dict):
        return msg
    if hasattr(msg, "model_dump"):
        return msg.model_dump()  # type: ignore[no-any-return]
    role = getattr(msg, "role", None)
    content = getattr(msg, "content", None)
    if role is not None:
        return {"role": str(role), "content": content}
    return {"raw": str(msg)[:2000]}


def _clip(text: str, n: int = 1200) -> str:
    text = text.strip()
    if len(text) <= n:
        return text
    return text[: n - 1] + "…"


def _summarize_content(content: Any) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    if content is None:
        return blocks
    if isinstance(content, str):
        return [{"kind": "text", "text": _clip(content)}]
    if not isinstance(content, list):
        return [{"kind": "other", "text": _clip(str(content))}]

    for block in content:
        if not isinstance(block, dict):
            blocks.append({"kind": "other", "text": _clip(str(block), 400)})
            continue
        if block.get("text") is not None:
            blocks.append({"kind": "text", "text": _clip(str(block["text"]))})
        elif "toolUse" in block or "tool_use" in block:
            tu = block.get("toolUse") or block.get("tool_use") or {}
            blocks.append(
                {
                    "kind": "tool_use_request",
                    "tool": tu.get("name") or tu.get("toolName"),
                    "toolUseId": tu.get("toolUseId") or tu.get("tool_use_id"),
                    "input": tu.get("input"),
                    "note": "Bedrock asked the host agent to run this tool (not executed inside Bedrock).",
                }
            )
        elif "toolResult" in block or "tool_result" in block:
            tr = block.get("toolResult") or block.get("tool_result") or {}
            payload_preview = ""
            parsed_status = None
            parsed_ids = None
            content_list = tr.get("content")
            if isinstance(content_list, list):
                for c in content_list:
                    if isinstance(c, dict) and c.get("text"):
                        payload_preview = _clip(str(c["text"]), 800)
                        try:
                            obj = json.loads(str(c["text"]))
                            if isinstance(obj, dict):
                                parsed_status = obj.get("status")
                                parsed_ids = obj.get("ids")
                        except json.JSONDecodeError:
                            pass
                        break
                    if isinstance(c, dict) and isinstance(c.get("json"), dict):
                        obj = c["json"]
                        payload_preview = _clip(json.dumps(obj), 800)
                        parsed_status = obj.get("status")
                        parsed_ids = obj.get("ids")
                        break
            blocks.append(
                {
                    "kind": "tool_result_from_host",
                    "toolUseId": tr.get("toolUseId") or tr.get("tool_use_id"),
                    "status": tr.get("status") or parsed_status,
                    "ids": parsed_ids,
                    "payloadPreview": payload_preview,
                    "note": "Executed on the host (local adapter HTTP), then sent back to Bedrock.",
                    "executedLocally": True,
                }
            )
        elif "reasoningContent" in block or "reasoning_content" in block:
            rc = block.get("reasoningContent") or block.get("reasoning_content")
            blocks.append({"kind": "reasoning", "text": _clip(str(rc), 600)})
        else:
            keys = ",".join(sorted(block.keys())[:8])
            blocks.append({"kind": "other", "text": f"block keys: {keys}"})
    return blocks


def build_turn_debug(
    *,
    agent_id: str,
    user_message: str,
    messages: list[Any],
    start_index: int,
    request_id: str,
    session_id: str,
) -> dict[str, Any]:
    slice_msgs = [_as_dict(m) for m in messages[start_index:]]
    turns: list[dict[str, Any]] = []
    tool_runs: list[dict[str, Any]] = []

    for msg in slice_msgs:
        role = str(msg.get("role") or "unknown")
        blocks = _summarize_content(msg.get("content"))
        turns.append({"role": role, "blocks": blocks})
        for b in blocks:
            if b.get("kind") == "tool_result_from_host":
                tool_runs.append(
                    {
                        "toolUseId": b.get("toolUseId"),
                        "status": b.get("status"),
                        "ids": b.get("ids"),
                        "executedLocally": True,
                        "payloadPreview": b.get("payloadPreview"),
                    }
                )
            if b.get("kind") == "tool_use_request":
                tool_runs.append(
                    {
                        "phase": "requested_by_bedrock",
                        "tool": b.get("tool"),
                        "toolUseId": b.get("toolUseId"),
                        "input": b.get("input"),
                    }
                )

    executed = any(r.get("executedLocally") for r in tool_runs)
    requested = any(r.get("phase") == "requested_by_bedrock" for r in tool_runs)

    debug: dict[str, Any] = {
        "requestId": request_id,
        "sessionId": session_id,
        "agentId": agent_id,
        "at": datetime.now(timezone.utc).isoformat(),
        "userMessage": user_message,
        "gatewayTools": os.environ.get("USE_GATEWAY_TOOLS", ""),
        "explanation": {
            "bedrock": "Host called Bedrock with conversation messages; Bedrock returned text and/or tool_use requests.",
            "tools": "Tools run in this host process (local adapters). Bedrock does not call PubMed/ChEMBL itself.",
            "proof": "tool_result blocks with status/ids prove host execution; UI tool_result (ok) lines are the same signal.",
        },
        "toolsRequestedByBedrock": requested,
        "toolsExecutedOnHost": executed,
        "toolActivity": tool_runs,
        "conversationDelta": turns,
    }
    return debug


def persist_turn_debug(debug: dict[str, Any]) -> str | None:
    try:
        _TURN_DIR.mkdir(parents=True, exist_ok=True)
        path = _TURN_DIR / f"{debug.get('requestId', 'turn')}.json"
        path.write_text(json.dumps(debug, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return str(path)
    except OSError:
        return None
