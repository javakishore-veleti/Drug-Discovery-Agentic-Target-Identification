"""Extract real tool / reasoning activity from Strands messages (Stories 4.3 / AD-5)."""

from __future__ import annotations

import json
from contextvars import ContextVar
from typing import Any

# Per-request forced tool failure (Story 4.3 simulation). Logical AD-3 name or "".
_force_tool_error: ContextVar[str] = ContextVar("force_tool_error", default="")

_EMPTY_IDS = {"pmid": [], "nct": [], "chembl": []}


def set_force_tool_error(tool_name: str | None) -> None:
    _force_tool_error.set((tool_name or "").strip().lower())


def get_force_tool_error() -> str:
    return _force_tool_error.get()


def forced_error_result(tool: str) -> dict[str, Any] | None:
    """Return AD-8/AD-9 error tool_result if this tool is being force-failed."""
    forced = get_force_tool_error()
    if not forced or forced != tool.strip().lower():
        return None
    return {
        "status": "error",
        "tool": tool,
        "message": f"Forced tool failure for smoke (Story 4.3): {tool}",
        "ids": dict(_EMPTY_IDS),
        "summary": "",
    }


def _as_dict(msg: Any) -> dict[str, Any]:
    if isinstance(msg, dict):
        return msg
    if hasattr(msg, "model_dump"):
        return msg.model_dump()  # type: ignore[no-any-return]
    role = getattr(msg, "role", None)
    content = getattr(msg, "content", None)
    if role is not None:
        return {"role": role, "content": content}
    return {}


def _parse_tool_result_payload(tool_result: dict[str, Any], *, tool_hint: str) -> dict[str, Any]:
    """Normalize Strands toolResult → Stream tool_result fields."""
    status_raw = (tool_result.get("status") or "").lower()
    status = "error" if status_raw in {"error", "failed"} else "ok"
    ids = dict(_EMPTY_IDS)
    summary = ""
    message = ""

    content = tool_result.get("content")
    texts: list[str] = []
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict):
                if block.get("text") is not None:
                    texts.append(str(block["text"]))
                elif "json" in block and isinstance(block["json"], dict):
                    texts.append(json.dumps(block["json"]))
            elif isinstance(block, str):
                texts.append(block)

    parsed: dict[str, Any] | None = None
    for text in texts:
        text = text.strip()
        if not text:
            continue
        try:
            obj = json.loads(text)
            if isinstance(obj, dict):
                parsed = obj
                break
        except json.JSONDecodeError:
            continue

    if parsed:
        if parsed.get("status") == "error":
            status = "error"
        elif parsed.get("status") == "ok":
            status = "ok"
        if isinstance(parsed.get("ids"), dict):
            for key in ("pmid", "nct", "chembl"):
                val = parsed["ids"].get(key)
                if isinstance(val, list):
                    ids[key] = [str(x) for x in val]
        summary = str(parsed.get("summary") or "")[:500]
        message = str(parsed.get("message") or "")[:300]
        tool_hint = str(parsed.get("tool") or tool_hint)

    if status == "error" and not message:
        message = "Tool returned an error"
    return {
        "type": "tool_result",
        "tool": tool_hint,
        "status": status,
        "ids": ids,
        "summary": summary,
        "message": message,
    }


def extract_activity_from_messages(
    messages: list[Any],
    *,
    start_index: int = 0,
) -> tuple[list[dict[str, Any]], list[str]]:
    """
    Walk new Strands messages and return (tool_events, reasoning_texts).

    tool_events are Stream-shaped ``tool_use`` / ``tool_result`` dicts in order.
    reasoning_texts are only non-empty when the model emitted reasoningContent (AD-5).
    """
    tool_events: list[dict[str, Any]] = []
    reasoning: list[str] = []
    # Map toolUseId → tool name for pairing results
    use_names: dict[str, str] = {}

    for msg in messages[start_index:]:
        m = _as_dict(msg)
        content = m.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue

            rc = block.get("reasoningContent")
            if isinstance(rc, dict):
                text = rc.get("reasoningText") or rc.get("text")
                if isinstance(text, dict):
                    text = text.get("text")
                if text and str(text).strip():
                    reasoning.append(str(text).strip())

            tu = block.get("toolUse")
            if isinstance(tu, dict) and tu.get("name"):
                name = str(tu["name"])
                tid = str(tu.get("toolUseId") or "")
                if tid:
                    use_names[tid] = name
                inp = tu.get("input")
                input_summary: Any = inp
                if isinstance(inp, dict):
                    # Keep small, non-secret summary for Stream Event
                    input_summary = {
                        k: (str(v)[:120] if not isinstance(v, (int, float, bool)) else v)
                        for k, v in list(inp.items())[:8]
                    }
                tool_events.append(
                    {
                        "type": "tool_use",
                        "tool": name,
                        "toolUseId": tid or None,
                        "input": input_summary,
                    }
                )

            tr = block.get("toolResult")
            if isinstance(tr, dict):
                tid = str(tr.get("toolUseId") or "")
                tool_name = use_names.get(tid, "unknown")
                tool_events.append(_parse_tool_result_payload(tr, tool_hint=tool_name))

    return tool_events, reasoning
