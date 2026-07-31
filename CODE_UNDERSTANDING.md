# Code understanding — local Stream path

How a single research turn flows from the Vite UI through host FastAPI into a Strands agent and Amazon Bedrock (local stack: `VITE_STACK_MODE=local`).

> Research assistance only. Not medical advice or clinical decision support.

## Table of contents

- [One-line call chain](#one-line-call-chain)
- [Key files](#key-files)
- [1. FastAPI entrypoint](#1-fastapi-entrypoint)
- [2. How the agent is invoked](#2-how-the-agent-is-invoked)
- [3. Where Bedrock is wired and invoked](#3-where-bedrock-is-wired-and-invoked)
- [4. What happens after `agent(message)` returns](#4-what-happens-after-agentmessage-returns)
- [5. Tools vs Bedrock](#5-tools-vs-bedrock)
- [6. Related docs](#6-related-docs)

## One-line call chain

`POST /` → `_build_sse` → `agent(message)` → Strands loop → `agent.model.stream()` (`TracedBedrockModel` → `BedrockModel`) → Bedrock → host tools if requested → SSE back to UI.

## Key files

| File | Role |
| --- | --- |
| [`local/stream_app.py`](local/stream_app.py) | FastAPI Stream on `:8787`; `POST /` builds SSE for one turn |
| [`local/agent_registry.py`](local/agent_registry.py) | `agentId` → `create_agent_by_id` (unified + specialists) |
| [`local/traced_bedrock.py`](local/traced_bedrock.py) | Wraps Strands `BedrockModel.stream()` for per-call tracing |
| [`local/bedrock_trace.py`](local/bedrock_trace.py) | Latest-turn Bedrock call viewer (`/bedrock-trace`) |
| [`agents/framework/base_agent.py`](agents/framework/base_agent.py) | Specialist factory: `BedrockModel` + system prompt + tools |
| [`agents/unified-research-agent/unified_research_agent/agent.py`](agents/unified-research-agent/unified_research_agent/agent.py) | Unified agent factory (same Bedrock + tools pattern) |
| [`web/`](web/) | Vite UI; POSTs JSON `{ message, sessionId?, agentId }` to Stream |

## 1. FastAPI entrypoint

**File:** [`local/stream_app.py`](local/stream_app.py)

- App object: `app = FastAPI(...)` near the top of the file.
- HTTP start of a turn: **`POST /`** → `stream_turn`.

```python
@app.post("/")
async def stream_turn(request: Request) -> PlainTextResponse:
    request_id = str(uuid.uuid4())
    # body: message / prompt / query, sessionId, agentId
    ...
    sse = _build_sse(session_id, message, request_id, agent_id)
    return PlainTextResponse(
        content=sse,
        media_type="text/event-stream; charset=utf-8",
        ...
    )
```

That is the starting point from the UI (Vite POSTs here on `http://127.0.0.1:8787/`).

Other useful routes on the same app:

| Route | Purpose |
| --- | --- |
| `GET /health` | Liveness + agent list |
| `GET /agents` | Available `agentId`s |
| `GET /bedrock-trace` | HTML viewer for Bedrock calls in the latest turn |
| `GET /bedrock-trace.json` | Same data as JSON |

## 2. How the agent is invoked

Still in [`local/stream_app.py`](local/stream_app.py), `_build_sse` loads or reuses the agent, then calls it like a function:

```python
agent = _agent_for(session_id, agent_id)
TRACE.begin_turn(...)
start = len(getattr(agent, "messages", []) or [])
result = agent(message)   # Strands sync turn API
```

### `_agent_for`

1. Looks up `session_id` in an in-memory `_sessions` dict.
2. If missing or `agent_id` changed → `create_agent_by_id(agent_id)` from [`local/agent_registry.py`](local/agent_registry.py).
3. Wraps `agent.model` with `TracedBedrockModel` (local tracing only).

`agent(message)` is Strands’ sync turn API: it runs the full **plan → tool_use → tool_result → Bedrock again** loop inside the agent until a final text answer (no further `tool_use`).

**Important:** every local `agentId` uses the **same Bedrock model and same tools**; specialists differ mainly by **system prompt**.

## 3. Where Bedrock is wired and invoked

### Created here (model attached to the agent)

**Unified:**

[`agents/unified-research-agent/unified_research_agent/agent.py`](agents/unified-research-agent/unified_research_agent/agent.py) — builds `BedrockModel(...)` and passes it into `strands.Agent`.

**Specialists:**

[`agents/framework/base_agent.py`](agents/framework/base_agent.py) — same pattern in `create_research_agent`:

```python
model = BedrockModel(
    model_id=get_bedrock_model_id(),
    region_name=get_aws_region(),
)
return Agent(
    model=model,
    system_prompt=system_prompt,
    tools=...,
)
```

### Actual network call to Bedrock

Not written by hand in this repo. Strands’ `BedrockModel.stream()` (from the `strands` package) performs the Bedrock API call when the agent runs.

### Local wrapper around that call

[`local/traced_bedrock.py`](local/traced_bedrock.py) — `TracedBedrockModel.stream()` calls `super().stream(...)` (real Bedrock) while recording each invocation for `/bedrock-trace`:

```python
async def stream(...):
    call = TRACE.start_call(...)
    try:
        async for event in super().stream(...):  # real Bedrock
            TRACE.note_event(call, event)
            yield event
    finally:
        TRACE.finish_call(call, error=err)
```

Host AWS credentials (`AWS_*` / profile / `~/.aws`) are used for Bedrock only — not for PubMed/ChEMBL public HTTP.

## 4. What happens after `agent(message)` returns

Still inside `_build_sse` in [`local/stream_app.py`](local/stream_app.py):

1. `extract_activity_from_messages(...)` walks the agent’s message history for this turn.
2. Emits SSE: `tool_use` / `tool_result` (and `error` on tool failure).
3. Chunks the final answer as SSE `token` events.
4. Optionally emits SSE `debug` (turn debug + Bedrock call count).
5. Always ends with SSE `done`.

The UI paints those events into the transcript. Live citation IDs appear when `tool_result` status is `ok`.

## 5. Tools vs Bedrock

| Step | Who | What |
| --- | --- | --- |
| Plan / decide tools | Bedrock (via Strands) | May return `tool_use` instead of a finished answer |
| Run PubMed / CT.gov / ChEMBL / Open Targets | **Host** process (in-process adapters) | HTTP to public APIs; Gateway MCP forced off locally |
| Synthesize answer | Bedrock again | Reads `tool_result`s; may request more tools or return final text |

Bedrock does **not** call PubMed itself. A `tool_use` is an instruction back to the Mac/host. There is no hard per-agent tool budget; the loop stops when Bedrock returns text without another tool instruction.

## 6. Related docs

- [`README.md`](README.md) — purpose, agents table, local sequence diagram (UI → FastAPI → Bedrock → UI)
- [`docs/local-stack.md`](docs/local-stack.md) — how to run `local:stream-and-ui-up`
- UI help popup — “What happens after you enter the prompt below” (`web/src/chat/ArchitectureModal.tsx`)
