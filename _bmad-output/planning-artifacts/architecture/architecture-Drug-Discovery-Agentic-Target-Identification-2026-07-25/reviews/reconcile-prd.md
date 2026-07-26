# PRD ↔ Architecture Spine Reconciliation

**Date:** 2026-07-25  
**Inputs:**
- PRD: `_bmad-output/planning-artifacts/prds/prd-Drug-Discovery-Agentic-Target-Identification-2026-07-25/prd.md`
- Addendum: `_bmad-output/planning-artifacts/prds/prd-Drug-Discovery-Agentic-Target-Identification-2026-07-25/addendum.md`
- Spine: `_bmad-output/planning-artifacts/architecture/architecture-Drug-Discovery-Agentic-Target-Identification-2026-07-25/ARCHITECTURE-SPINE.md`

**Scope:** Material gaps only — PRD requirements not covered by an AD, consistency convention, or explicit Deferred entry, or direct contradictions. Non-material / story-level items noted briefly at end.

---

## Executive Summary

| Metric | Result |
| --- | --- |
| FRs (FR-1..FR-21) | 21/21 covered (explicit AD, convention, capability map, or Deferred) |
| NFRs (NFR-1..NFR-13) | 13/13 covered (AD, convention, or appropriately non-architectural soft expectation) |
| Addendum reconcile items (§J) | Aligned; prior brief/README deltas already dispositioned |
| PRD Open Questions (#1–#5) | #1, #3, #4 resolved in spine; #2 in PRD/NFR-9; #5 in Deferred |
| **Material gaps** | **1** |
| **Contradictions** | **0** |

---

## Coverage Matrix (FR)

| FR | Requirement (short) | Spine coverage |
| --- | --- | --- |
| FR-1 | Cognito email/password sign-in | AD-10; auth convention |
| FR-2 | Manual admin user provisioning | AD-10, AD-11 (Outputs + docs) |
| FR-3 | Start Chat Session, send message | AD-4; `web/` capability map |
| FR-4 | Stream Event contract (7 types + optional `reasoning`) | AD-4, AD-5; Stream Event conventions |
| FR-5 | Tool-use visibility in UI | AD-4 (`tool_use` convention) |
| FR-6 | Research Disclaimer always visible | AD-14 (binds FR-6); addendum §F in spine `sources` |
| FR-7 | Sign out | Implicit: AD-10 (Cognito session) + AD-1 (unauthenticated stream rejected) |
| FR-8 | Browser never invokes Runtime directly | AD-1 |
| FR-9 | Tool failure → `error`; session continues | AD-8 |
| FR-10 | Multi-domain synthesis (Herceptin demo) | AD-2, AD-6; capability map “Herceptin demo path” |
| FR-11 | Surface PMID / NCT / ChEMBL when returned | AD-9; ID pass-through convention |
| FR-12 | Research-assist behavioral boundary | AD-14 (system prompt + Disclaimer) |
| FR-13 | PubMed via Gateway | AD-3 |
| FR-14 | ClinicalTrials.gov via Gateway | AD-3 |
| FR-15 | ChEMBL via Gateway | AD-3 |
| FR-16 | Exactly three V1 tools | AD-3; Deferred table (tools 4+) |
| FR-17 | In-session follow-up memory | AD-7 |
| FR-18 | CDK deploy full slice | AD-11; Stack; structural seed |
| FR-19 | Documented CDK Outputs | AD-11 (named Outputs convention) |
| FR-20 | CDK destroy cleans app stacks | AD-11; Deferred (bootstrap leftovers noted) |
| FR-21 | Install/deploy/destroy/docs | AD-11 (`docs/` in structural seed) |

---

## Coverage Matrix (NFR)

| NFR | Requirement (short) | Spine coverage |
| --- | --- | --- |
| NFR-1 | No browser→Runtime direct invoke | AD-1 |
| NFR-2 | Cognito required for chat/stream | AD-10, AD-1 |
| NFR-3 | No secrets in repo; least privilege | AD-12; config convention |
| NFR-4 | No heavy WAF; HTTPS + Cognito baseline | Deferred (“Heavy WAF / CI polish”); Frontend stack S3+CloudFront |
| NFR-5 | Soft: first `tool_use` <30s Warm Path | Non-architectural soft demo expectation; no structural lever required |
| NFR-6 | Soft: answer often 1–3 min | Non-architectural soft demo expectation |
| NFR-7 | Not contractual SLA | Acknowledged; no AD needed |
| NFR-8 | Tool timeout/error streamed; chat continues | AD-8 |
| NFR-9 | Partial failure UX; 5 min stall terminal state | AD-8 (failure path); AD-4 (5 min stall) |
| NFR-10 | Basic debug logs (session/request/tool) | AD-12; logging convention |
| NFR-11 | No end-user audit export | Absence of feature; no AD required |
| NFR-12 | Destroy-when-idle operating model | AD-11; environments note |
| NFR-13 | Single cost-conscious region deploy | Stack + region convention |

---

## Addendum Cross-Check

| Section | Content | Spine status |
| --- | --- | --- |
| A | Reference request path | Matches Design Paradigm diagram and AD-1/AD-7 |
| B | Stream Event roles | AD-4, AD-5; payload shapes deferred to conventions (appropriate) |
| C | Memory mechanism options | Resolved: AD-7 selects AgentCore Memory |
| D | Public API rate limits / backoff | **Gap — see Material Gap #1** (ID formats partially in conventions) |
| E | Competitive stance | Product positioning; not architecture |
| F | Approved Disclaimer copy | Bound via AD-14 + spine `sources`; exact text not duplicated in conventions (acceptable) |
| G | Canonical demo prompts | Capability map + AD-9/AD-6 |
| H | Deferred tool backlog | Deferred table |
| I | Rejected V1 items | Aligned with spine Deferred / non-goals |
| J | Finalize dispositions | Brief/README deltas dispositioned; reviewer medium/low items addressed or story-deferred |

---

## PRD Open Questions — Disposition vs Spine

| # | Topic | PRD disposition | Spine resolution |
| --- | --- | --- | --- |
| 1 | Bedrock model ID pin | Deferred to architecture | **Resolved:** AD-6 pins `us.anthropic.claude-sonnet-4-20250514-v1:0` |
| 2 | Stream stall UI timeout | Resolved: 5 minutes | **Resolved:** AD-4 |
| 3 | `reasoning` emission | Deferred to architecture | **Resolved:** AD-5 (optional, never fabricated) |
| 4 | Log retention days | Deferred to architecture | **Resolved:** AD-12 (7 days) |
| 5 | Post-V1 tool #4 preference | Deferred to roadmap | **Resolved:** Deferred table |

---

## Material Gaps

### Gap 1 — Public API rate limits, throttling, and retry behavior (Addendum §D)

**PRD / addendum source:** Addendum §D documents PubMed (~3 req/s without key), ClinicalTrials.gov 429 backoff, and ChEMBL throttling as constraints on tool implementation and demo reliability. NFR-8 and the Herceptin demo path depend on tools surviving public API limits during multi-tool turns.

**Spine today:** AD-3 defines three Lambda MCP tools and AD-12 scopes IAM, but no AD or convention governs outbound HTTP resilience (rate limiting, exponential backoff on 429/503, timeouts aligned with AD-8 stream error surfacing).

**Partial coverage:** Consistency conventions specify ID pass-through formats (PMID, NCT, ChEMBL) from the same addendum section; rate-limit behavior is not mirrored.

**Recommendation (non-blocking for finalize):** Add a short AD or extend AD-3/AD-8 conventions — e.g., per-tool client timeout budget, 429 backoff for ClinicalTrials.gov, serial/throttled PubMed calls — so gateway tool stories inherit a single pattern.

**Severity:** Medium-low for V1 demoware, but material because omitting it can cause flaky SM-1/SM-4 demos without an architectural hook.

---

## Contradictions

None identified.

Checked areas:
- **Auth path:** PRD assumption (Cognito-authenticated Function URL + SigV4/IAM) compatible with AD-1 options (Identity Pool + SigV4 or JWT authorizer).
- **Memory:** PRD defers mechanism; AD-7 picks AgentCore Memory — consistent with addendum §C.
- **Error shapes:** PRD FR-9 allows `error` and/or `tool_result` + `error`; AD-8 canonicalizes both — stricter superset, not a conflict.
- **Tool count:** PRD FR-16 “exactly three” matches AD-3; addendum §J brief “3–5 tools” override acknowledged.
- **Model pin:** PRD deferred; AD-6 resolves — no conflict.
- **Reasoning:** PRD optional; AD-5 optional-only — aligned.

---

## Non-Material / Story-Level (not counted as gaps)

| Item | Notes |
| --- | --- |
| FR-7 sign-out | No dedicated AD; standard Cognito client behavior + AD-1 unauthenticated rejection suffices |
| NFR-5 / NFR-6 soft latency | Demo expectations without structural decisions |
| FR-12 negative test probes | Addendum §J → story/refinement; AD-14 states behavioral boundary |
| FR-6 Disclaimer UX placement | “Visible without separate legal page” — UX/story; AD-14 + addendum §F sufficient for architecture |
| NFR-9 partial multi-tool success synthesis | Agent notes gaps when some tools succeed; implied by AD-2 agent role; explicit prompt guidance belongs in agent stories |
| Observability smoke scenario | Addendum §J → AD-12 logging fields cover debug intent |
| SM-7 extensibility-in-a-day docs | Structural seed (`gateways/database/`) + AD-3 Lambda MCP pattern architecturally precludes blocking; doc pattern is FR-21/SM-6 scope |
| §9.3 IP guardrail (no copying proprietary sample code) | Process/implementation constraint; not a structural architecture decision — note in agent/tool story guardrails |
| SSE reconnect/heartbeat | Correctly in Deferred table |

---

## Verdict

Architecture spine is **substantially aligned** with the finalized PRD and addendum. All FRs and NFRs map to adopted ADs, conventions, capability placement, or appropriate deferral/non-architectural treatment.

**One material gap:** public API rate-limit / backoff / timeout behavior for the three Gateway Tool adapters (Addendum §D) is not yet an AD or convention.

**No contradictions** between PRD and spine.

---

## Suggested Next Step (optional)

Before epics/stories, add **AD-3 companion rule or convention row** for tool HTTP clients: timeouts, 429 backoff (ClinicalTrials.gov), and PubMed/ChEMBL throttling strategy — keeps demo reliability testable under NFR-8 without expanding V1 scope.
