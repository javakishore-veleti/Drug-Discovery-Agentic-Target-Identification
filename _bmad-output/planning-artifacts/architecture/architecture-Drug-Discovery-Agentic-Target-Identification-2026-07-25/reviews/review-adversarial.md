# Adversarial Architecture Review — ARCHITECTURE-SPINE.md

**Reviewer lens:** Construct two units one level down that each obey every AD literally yet still integrate incompatibly. Each pair is a spine hole requiring a new or tightened AD.

**Spine reviewed:** `ARCHITECTURE-SPINE.md` (draft, 2026-07-25)  
**Verdict:** **Conditional pass — five literal-compliance forks allow silent integration failure.** Spine fixes divergence at layer boundaries but leaves shared-entity ownership, envelope field semantics, and auth choice unspecified enough for two diligent teams to ship a broken demo.

---

## Incompatible Pairs (AD-compliant builds that clash)

### Pair 1 — Dual auth paths, zero handshake (web/ × Stream Lambda)

| Unit | Literal AD obedience | Build choice |
| --- | --- | --- |
| **web/** | AD-1, AD-10, Auth header convention | Cognito User Pool login → **Identity Pool credentials → SigV4** on Function URL POST |
| **Stream Lambda** (`infra/backend`) | AD-1, AD-12 | Function URL with **Cognito JWT authorizer**; expects `Authorization: Bearer <idToken>` |

**Clash:** Shared boundary is the Stream HTTP request. Both units satisfy AD-1 (“Preferred … SigV4 **or** JWT authorizer”). No AD names a **single** V1 auth mode or requires a shared contract artifact (OpenAPI / authorizer config checked into repo). **100% auth failure** with no Stream Events emitted.

**Hole type:** Clashing shared-data shape (request auth envelope).

**Close with:** **AD-1 tighten** — pick exactly one V1 mode (recommend JWT authorizer + Bearer idToken from User Pool client, or SigV4 — not both). Add: “The other mode is Deferred; `web/` and Stream Lambda MUST implement the same mode; authorizer config is owned by `infra/backend` and referenced by `web/` env at build time.”

---

### Pair 2 — Two owners of Chat Session identity (Stream Lambda × Agent Runtime + Memory)

| Unit | Literal AD obedience | Build choice |
| --- | --- | --- |
| **Stream Lambda** | AD-4 (`session_started`), AD-7, Logging `sessionId` | Generates `sessionId` (UUID) at SSE open; emits `session_started`; passes same id as **custom invoke header** |
| **Agent Runtime + Memory wiring** | AD-7 (“Memory **or** Runtime session binding”), AD-11 | Uses **AgentCore Runtime invoke `sessionId`** returned by API; Memory keyed only to Runtime id; ignores custom header |

**Clash:** Two entities named “session” with no AD declaring **canonical session key**. Stream events and logs use Stream-owned id; Memory turns attach to Runtime-owned id. UI shows consistent `session_started` while **multi-turn context is empty or wrong** — AD-7 satisfied in letter (“persist … for one Chat Session”) but not in integration.

**Hole type:** Two owners of one entity (Chat Session / sessionId).

**Close with:** **AD-7 tighten** — “Exactly one canonical `sessionId` for a Chat Session: the AgentCore Runtime session id returned on invoke. Stream Lambda MUST obtain/create via Runtime invoke API, emit it in `session_started`, and MUST NOT mint an independent id. Memory and structured logs MUST use this same value.”

---

### Pair 3 — Tool payload shapes vs agent citation extraction (gateways/database × unified-research-agent)

| Unit | Literal AD obedience | Build choice |
| --- | --- | --- |
| **Tool Lambdas** (`pubmed`, `clinicaltrials`, `chembl`) | AD-3, AD-8, AD-9, ID conventions (“pass through, do not invent”) | Each returns **native API JSON** embedded in MCP content: e.g. PubMed `{ "esearchresult": { "idlist": ["123"] } }`, CT `{ "studies": [{ "protocolSection": { "identificationModule": { "nctId": "NCT01234567" } } }] }`, ChEMBL `{ "molecules": [{ "molecule_chembl_id": "CHEMBL25" }] }` |
| **Unified Research Agent** | AD-9 (“when tool payloads **include** PMID / NCT / ChEMBL ID, answer must include them”) | Prompt + parser expect **flat** fields `pmid`, `nct_id`, `chembl_id` on a normalized object in `tool_result.summary` |

**Clash:** Shared-data shape at the tool→agent seam. Tools “include” IDs (AD-9 ✓); agent cannot find them in nested vendor shapes (AD-9 ✓ — “absence … is not a turn failure”). **Ungrounded answers despite compliant tools** — SM-4 / FR-11 fail in practice while every AD passes review.

**Hole type:** Clashing shared-data shapes (tool MCP payload / summary schema).

**Close with:** **New AD-15 (Tool result schema)** — “Each MCP tool MUST return a V1-normalized envelope: `{ "records": [ { "source": "pubmed"|"clinicaltrials"|"chembl", "id": "<canonical id per ID conventions>", "title"?: string, "snippet"?: string } ] }` plus optional `raw` passthrough. Gateway/tool Lambdas own normalization; agent MUST NOT scrape vendor JSON. `tool_result.summary` on the stream MAY mirror `records` truncated.”

---

### Pair 4 — Conflicting terminal-state mutation on tool failure (Stream Lambda × Agent Runtime)

| Unit | Literal AD obedience | Build choice |
| --- | --- | --- |
| **Stream Lambda** | AD-8, AD-4 | On Gateway timeout: emit `tool_result` (`status: error`), `error`, then **`done` immediately** and **close SSE** — interprets “when the agent finishes **or aborts** synthesis” as abort on tool hard-fail |
| **Unified Research Agent** | AD-8, AD-2 | Strands loop **continues after tool error**; model synthesizes from partial context; runtime stream still emits **`token`** deltas afterward |

**Clash:** Conflicting state-mutation paths for the same turn. Stream Lambda declares turn terminal (`done`, connection closed); agent still produces answer tokens. UI either **misses the synthesis** or receives **events after `done`** (violates AD-4 soft-stall / terminal semantics in spirit). Both cite AD-8’s “still emit `done` … when agent finishes or aborts” with opposite readings of who decides abort.

**Hole type:** Conflicting state-mutation paths (turn lifecycle / SSE terminal state).

**Close with:** **AD-8 tighten** — “Stream Lambda owns SSE lifecycle. It MUST NOT emit `done` until the Runtime invoke stream ends (success, agent abort, or unrecoverable bridge error). On tool `status: error`, emit `tool_result` + `error` but **keep bridging** until Runtime stream completes. Agent SHOULD continue synthesis unless operator policy says otherwise; if agent aborts, Runtime ends stream first, then Lambda emits `done`.” Optionally: AD-4 add `turn_aborted` vs `done` if distinction needed.

---

### Pair 5 — Memory config env split (infra/backend CDK × unified-research-agent)

| Unit | Literal AD obedience | Build choice |
| --- | --- | --- |
| **infra/backend** (CDK) | AD-7, AD-11, AD-12, Config convention | Creates AgentCore Memory; injects **`AGENTCORE_MEMORY_ID`** on Runtime task env from stack output |
| **unified-research-agent** | AD-7, AD-13, Config convention | Reads **`MEMORY_ID`** (Strands/AgentCore sample default) or relies on **undocumented Runtime auto-bind** with no env set |

**Clash:** Memory resource exists and IAM allows R/W (AD-12 ✓); agent never opens the configured Memory id. **Single-turn amnesia** while AD-7 reads satisfied (“wired in Runtime + infra”). Two owners of “how Memory is bound”: CDK vs agent bootstrap — no AD assigns the env var name or startup contract.

**Hole type:** Two owners of one entity (Memory binding); clashing config shape.

**Close with:** **AD-7 + Config row tighten** — “Canonical env var: `AGENTCORE_MEMORY_ID` (required on Runtime). Agent entrypoint MUST read it and call Memory APIs before accepting turns. CDK MUST set the same name; agent MUST NOT use alternate aliases. Add to AD-11 Outputs: `MemoryId` for operators.”

---

## Additional literal-compliance forks (not counted in top 5)

- **tool_use.input size:** Stream Lambda emits full MCP args; web/ assumes short summary — AD-4 “may include input summary” allows both; UI lockup on large PubMed queries.
- **reasoning interleaving:** Stream Lambda forwards Strands thinking as it arrives; web/ assumes reasoning block completes before tokens — AD-5 allows both; scrambled UI.
- **Stream Lambda runtime:** Stack assumption Python 3.12 vs Node 22 — both AD-12 compliant; duplicated auth helpers diverge.

These are lower severity if Pair 1 auth is fixed first.

---

## Summary Table

| # | Units | Clash | Missing spine lock |
| --- | --- | --- | --- |
| 1 | web/ ↔ Stream Lambda | Auth envelope | Single V1 auth mode |
| 2 | Stream Lambda ↔ Runtime/Memory | sessionId ownership | Canonical session key |
| 3 | Tool Lambdas ↔ Agent | Tool JSON shape | Normalized tool result schema |
| 4 | Stream Lambda ↔ Agent | Turn terminal / `done` timing | Bridge owns lifecycle until Runtime EOF |
| 5 | CDK ↔ Agent | Memory env var | Named binding contract |

---

## Recommended spine actions

1. Tighten **AD-1** (auth — pick one).
2. Tighten **AD-7** (session id + Memory env).
3. Add **AD-15** (tool result normalized schema).
4. Tighten **AD-8** (do not early-`done` on tool error).
5. Extend **AD-11 Outputs** with `MemoryId` and auth mode documentation pointer.

Until these land, two AD-literal teams can pass checklist review and still fail the Herceptin demo path (AD-9 / capability map).
