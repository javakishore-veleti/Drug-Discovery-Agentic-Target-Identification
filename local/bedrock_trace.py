"""
Live Bedrock call tracer for local Stream (latest turn only — no history).

Each agent step that talks to Bedrock is one traced call. PubMed/ChEMBL HTTP
on your Mac between calls is NOT a Bedrock call.
"""

from __future__ import annotations

import html
import json
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
_OUT_DIR = _REPO / ".local-run"
_HTML_PATH = _OUT_DIR / "bedrock-trace-latest.html"
_JSON_PATH = _OUT_DIR / "bedrock-trace-latest.json"
_lock = threading.Lock()


def _clip(text: str, n: int = 900) -> str:
    text = (text or "").strip()
    if len(text) <= n:
        return text
    return text[: n - 1] + "…"


def _summarize_messages(messages: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not messages:
        return out
    for msg in list(messages)[-12:]:
        if isinstance(msg, dict):
            role = str(msg.get("role") or "?")
            content = msg.get("content")
        else:
            role = str(getattr(msg, "role", "?"))
            content = getattr(msg, "content", None)
        kinds: list[str] = []
        preview = ""
        if isinstance(content, str):
            preview = _clip(content, 400)
            kinds.append("text")
        elif isinstance(content, list):
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get("text"):
                    kinds.append("text")
                    if not preview:
                        preview = _clip(str(block["text"]), 400)
                elif "toolUse" in block or "tool_use" in block:
                    tu = block.get("toolUse") or block.get("tool_use") or {}
                    kinds.append(f"toolUse:{tu.get('name') or '?'}")
                elif "toolResult" in block or "tool_result" in block:
                    kinds.append("toolResult")
        out.append({"role": role, "kinds": kinds or ["?"], "preview": preview})
    return out


@dataclass
class BedrockCall:
    index: int
    started_at: str
    model_id: str
    message_count: int
    messages_summary: list[dict[str, Any]]
    tool_spec_count: int
    finished_at: str | None = None
    duration_ms: float | None = None
    event_count: int = 0
    saw_tool_use: bool = False
    saw_text: bool = False
    error: str | None = None
    _t0: float = field(default=0.0, repr=False)


@dataclass
class TraceTurn:
    request_id: str
    session_id: str
    agent_id: str
    model_id: str
    started_at: str
    finished_at: str | None = None
    user_message: str = ""
    calls: list[BedrockCall] = field(default_factory=list)


class BedrockTraceStore:
    def __init__(self) -> None:
        self._turn: TraceTurn | None = None

    def begin_turn(
        self,
        *,
        request_id: str,
        session_id: str,
        agent_id: str,
        model_id: str,
        user_message: str,
    ) -> None:
        with _lock:
            self._turn = TraceTurn(
                request_id=request_id,
                session_id=session_id,
                agent_id=agent_id,
                model_id=model_id,
                started_at=datetime.now(timezone.utc).isoformat(),
                user_message=_clip(user_message, 500),
            )
            self._persist_unlocked()

    def start_call(
        self,
        *,
        messages: Any,
        tool_specs: Any,
        model_id: str,
    ) -> BedrockCall:
        with _lock:
            if self._turn is None:
                self._turn = TraceTurn(
                    request_id="adhoc",
                    session_id="",
                    agent_id="?",
                    model_id=model_id,
                    started_at=datetime.now(timezone.utc).isoformat(),
                )
            call = BedrockCall(
                index=len(self._turn.calls) + 1,
                started_at=datetime.now(timezone.utc).isoformat(),
                model_id=model_id,
                message_count=len(list(messages or [])),
                messages_summary=_summarize_messages(messages),
                tool_spec_count=len(list(tool_specs or [])),
                _t0=time.perf_counter(),
            )
            self._turn.calls.append(call)
            self._persist_unlocked()
            return call

    def note_event(self, call: BedrockCall, event: Any) -> None:
        call.event_count += 1
        text = str(event)
        low = text.lower()
        if "tooluse" in low or "tool_use" in low:
            call.saw_tool_use = True
        if '"text"' in text or "'text'" in text:
            call.saw_text = True

    def finish_call(self, call: BedrockCall, error: str | None = None) -> None:
        with _lock:
            call.finished_at = datetime.now(timezone.utc).isoformat()
            call.duration_ms = round((time.perf_counter() - call._t0) * 1000, 1)
            call.error = error
            self._persist_unlocked()

    def end_turn(self) -> dict[str, Any]:
        with _lock:
            if self._turn is None:
                return {"status": "idle", "calls": [], "bedrockCallCount": 0}
            self._turn.finished_at = datetime.now(timezone.utc).isoformat()
            data = self._as_dict_unlocked()
            self._persist_unlocked()
            return data

    def as_dict(self) -> dict[str, Any]:
        with _lock:
            return self._as_dict_unlocked()

    def _as_dict_unlocked(self) -> dict[str, Any]:
        t = self._turn
        if t is None:
            return {
                "status": "idle",
                "calls": [],
                "bedrockCallCount": 0,
                "note": (
                    "Each call is one Bedrock model invocation from your Mac. "
                    "PubMed/ChEMBL HTTP runs on your Mac between calls and is not a Bedrock call."
                ),
            }
        return {
            "status": "done" if t.finished_at else "running",
            "requestId": t.request_id,
            "sessionId": t.session_id,
            "agentId": t.agent_id,
            "modelId": t.model_id,
            "startedAt": t.started_at,
            "finishedAt": t.finished_at,
            "userMessage": t.user_message,
            "bedrockCallCount": len(t.calls),
            "calls": [
                {
                    "index": c.index,
                    "startedAt": c.started_at,
                    "finishedAt": c.finished_at,
                    "durationMs": c.duration_ms,
                    "modelId": c.model_id,
                    "messageCount": c.message_count,
                    "toolSpecCount": c.tool_spec_count,
                    "eventCount": c.event_count,
                    "sawToolUse": c.saw_tool_use,
                    "sawText": c.saw_text,
                    "error": c.error,
                    "messagesSummary": c.messages_summary,
                }
                for c in t.calls
            ],
            "note": (
                "Each call is one Bedrock model invocation from your Mac. "
                "PubMed/ChEMBL HTTP runs on your Mac between calls and is not a Bedrock call."
            ),
        }

    def render_html(self) -> str:
        return html_from_trace_data(self.as_dict())

    def _persist_unlocked(self) -> None:
        try:
            _OUT_DIR.mkdir(parents=True, exist_ok=True)
            data = self._as_dict_unlocked()
            _JSON_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            _HTML_PATH.write_text(html_from_trace_data(data), encoding="utf-8")
        except OSError:
            return


def html_from_trace_data(data: dict[str, Any]) -> str:
    calls = data.get("calls") or []
    rows: list[str] = []
    for c in calls:
        kinds: list[str] = []
        if c.get("sawToolUse"):
            kinds.append("asked for tool(s)")
        if c.get("sawText"):
            kinds.append("returned text")
        if c.get("error"):
            kinds.append(f"error: {c['error']}")
        msg_bits: list[str] = []
        for m in c.get("messagesSummary") or []:
            msg_bits.append(
                f"<li><code>{html.escape(str(m.get('role')))}</code> "
                f"{html.escape(','.join(m.get('kinds') or []))} "
                f"<div class='prev'>{html.escape(str(m.get('preview') or ''))}</div></li>"
            )
        rows.append(
            f"""
<article class="call">
  <h2>Bedrock call #{c.get('index')} · {html.escape(str(c.get('durationMs') or '…'))} ms</h2>
  <p><strong>Model:</strong> <code>{html.escape(str(c.get('modelId') or ''))}</code></p>
  <p><strong>Messages in:</strong> {c.get('messageCount')} ·
     <strong>Tool specs offered:</strong> {c.get('toolSpecCount')} ·
     <strong>Stream events:</strong> {c.get('eventCount')}</p>
  <p><strong>Outcome signals:</strong> {html.escape(', '.join(kinds) or 'in progress…')}</p>
  <details open>
    <summary>Messages sent into this Bedrock call (summary)</summary>
    <ol>{''.join(msg_bits) or '<li>(none)</li>'}</ol>
  </details>
</article>
"""
        )
    status = html.escape(str(data.get("status") or "idle"))
    body = "\n".join(rows) or "<p class='empty'>No Bedrock calls yet this turn.</p>"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Bedrock call trace (latest)</title>
  <style>
    body {{ font-family: "IBM Plex Sans", system-ui, sans-serif; margin: 1rem;
           background: #f6f4ef; color: #1c2430; }}
    h1 {{ font-family: "IBM Plex Serif", Georgia, serif; font-size: 1.2rem; }}
    .banner {{ background: #eef6f1; border: 1px solid #9bb8a8; padding: .7rem .85rem; margin-bottom: 1rem; }}
    .call {{ background: #fffdf8; border: 1px solid #d7d2c8; padding: .75rem; margin: .75rem 0; }}
    .prev {{ color: #5b6573; font-size: .85rem; white-space: pre-wrap; margin-top: .2rem; }}
    code {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .85em; }}
    .empty {{ color: #5b6573; }}
  </style>
</head>
<body>
  <h1>Bedrock call trace · latest turn only</h1>
  <div class="banner">
    <p><strong>Status:</strong> {status} ·
       <strong>Calls this turn:</strong> {data.get('bedrockCallCount', 0)} ·
       <strong>Model:</strong> <code>{html.escape(str(data.get('modelId') or ''))}</code> ·
       <strong>Agent:</strong> <code>{html.escape(str(data.get('agentId') or ''))}</code></p>
    <p>{html.escape(str(data.get('note') or ''))}</p>
    <p><strong>User message:</strong> {html.escape(str(data.get('userMessage') or ''))}</p>
    <p class="empty">Snapshot for the latest Send only (no auto-refresh, no history).</p>
  </div>
  {body}
</body>
</html>
"""


TRACE = BedrockTraceStore()


def render_trace_html() -> str:
    return TRACE.render_html()
