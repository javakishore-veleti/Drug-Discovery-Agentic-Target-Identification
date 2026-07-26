# Architecture Spine Rubric Review

**Document:** `ARCHITECTURE-SPINE.md`  
**Reviewed:** 2026-07-25  
**Rubric:** good-spine checklist (initiative altitude, V1 demoware vertical slice)  
**Sources cross-checked:** PRD (`prd.md`, `addendum.md`), `README.md`

---

## Overall Verdict: **adequate**

The spine is lean, PRD-aligned, and closes most cross-unit forks that would break a Herceptin demo (stream contract, three tools, secure bridge, CDK topology, memory scope). It is not **strong** because one high-stakes auth fork remains undecided in an adopted AD, and a few PRD capabilities lack enforceable rules. Nothing is **broken** for demoware scope; gaps are refinements, not rebuilds.

| Severity | Count |
| --- | --- |
| critical | 0 |
| high | 2 |
| medium | 6 |
| low | 5 |

---

## Checklist Walk

### 1. Fixes real divergence points for the level below; misses none that matter

**Pass (with gaps).** AD-1–AD-14 plus Consistency Conventions lock the forks that would split `web/`, stream handler, agent, tools, and `infra/` during a vertical slice:

| Divergence domain | Governed by | Assessment |
| --- | --- | --- |
| Browser → Runtime security boundary | AD-1, AD-13 | Strong, except auth mechanism fork (see H-1) |
| Single agent vs swarm | AD-2 | Closed |
| V1 tool count / names | AD-3, conventions | Closed |
| SSE / Stream Event contract | AD-4, AD-5, AD-8, conventions | Strong |
| Model pin / region | AD-6, Stack, conventions | Closed (Open Q #1 resolved) |
| Session memory scope | AD-7 | Closed |
| Tool failure semantics | AD-8 | Closed |
| Source ID surfacing | AD-9 | Rule present; enforcement weak (M-3) |
| Auth provisioning model | AD-10 | Closed |
| CDK stacks / outputs / destroy | AD-11, AD-12 | Closed |
| Package dependency direction | AD-13 | Closed |
| Data / PHI boundary | AD-14 | Partial for FR-12 (H-2) |

**Misses that matter:**

- **H-1:** Stream UI auth is two incompatible patterns in one adopted rule (Identity Pool + SigV4 *or* JWT authorizer). `web/` and `infra/backend` can ship against different choices without violating the spine.
- **H-2 / M-1:** FR-3 (empty submit guard), FR-7 (sign out), FR-12 (agent behavioral boundary) have no dedicated, testable AD — only capability-map mentions or prompt hand-waving in AD-14.
- **M-2:** NFR-5/6/7 (Warm Path timing soft expectations) are neither decided nor listed Open/Deferred; epics may omit demo smoke timing entirely.

Non-blocking for demoware: tool per-call timeout values, CORS details, Bedrock access failure messaging (PRD UJ-2 edge case).

---

### 2. Every AD's Rule is enforceable and prevents its stated divergence

| AD | Enforceable? | Notes |
| --- | --- | --- |
| AD-1 | **Partial** | “Only Stream Lambda invokes Runtime” is enforceable (IAM + no client SDK). Auth sub-rule is not — two valid implementations (H-1). |
| AD-2 | Yes | Single runtime entrypoint; CI/repo layout can grep for extra agents. |
| AD-3 | Yes | Gateway config + deploy smoke = exactly three MCP tools. |
| AD-4 | Yes | Typed SSE contract; UI ignores unknown types; 5‑min stall in AD-4. |
| AD-5 | Yes | Omit-only rule; no fabrication. Lacks `[ADOPTED]` tag (L-1) — semantic only. |
| AD-6 | Yes | Pinned model id in agent config + CDK context. |
| AD-7 | Yes | No session-list UI; memory scoped to Chat Session. |
| AD-8 | Yes | Concrete event sequence: `tool_result` error → `error` → session continues → `done`. |
| AD-9 | **Partial** | “Must include” PMIDs/NCT/ChEMBL depends on prompt compliance; no structural check (M-3). |
| AD-10 | Yes | Cognito admin-provisioned; no self-signup UI. |
| AD-11 | Yes | Two-stack topology + named Outputs; destroy documented. |
| AD-12 | Yes | Scoped IAM + 7-day log retention (Open Q #4 resolved). |
| AD-13 | Yes | Dependency diagram + import rules. |
| AD-14 | **Partial** | Public APIs + disclaimer boundary stated; FR-12 negative probes (no dosing orders) not rule-bound (H-2). |

---

### 3. Nothing under Deferred could let two units diverge dangerously

**Pass (mostly).** Deferred items correctly defer README catalog tools, SSO, session list, WAF/CI, UX polish, and diagram depth — all PRD non-goals.

| Deferred item | Divergence risk | Verdict |
| --- | --- | --- |
| SSE reconnect/heartbeat | Low if AD-4 types hold | Safe — explicitly noted |
| Tools 4–5, multi-agent, SSO | Scope deferral | Safe |
| Vite vs bundler | Low — Stack assumption | Safe |
| Model fallback automation | Manual pin swap per AD-6 | Safe for demoware |
| UX design system | Presentation only | Safe |

**Not in Deferred but still fork-prone:** AD-1 auth OR (H-1) — should be **Decided** or **Deferred with “pick one before web+infra stories”**, not left as dual preferred paths in an adopted AD.

---

### 4. Named tech is verified-current

**Pass.** Stack table dated 2026-07-25; spot-checks against public registries/docs:

| Name | Spine value | Verification |
| --- | --- | --- |
| `aws-cdk-lib` | ^2.262 | Real release (2026-07-22); 2.262.1 exists — pin is current, not invented |
| `strands-agents` | ^1.47 | PyPI 1.47.0 (2026-07-10) — current |
| Bedrock model | `us.anthropic.claude-sonnet-4-20250514-v1:0` | AWS model card geo-inference ID — real, not invented |
| Node.js | 22.x | Matches README prerequisites |
| Python | 3.12 | Matches README |
| AgentCore (Runtime/Gateway/Memory) | managed + CDK constructs | Qualifier “as available in aws-cdk-lib 2.262” is honest |
| React + Vite 18+ | `[ASSUMPTION]` | Reasonable; not falsely pinned |
| Stream Lambda runtime | Python 3.12 `[ASSUMPTION]` | Open Assumption #4 — acceptable |

**Low notes:**

- **L-2:** Stack pins `aws-cdk-lib` but not CDK CLI version; post-2025 CLI/library version lines diverge — docs should say “latest 2.x CLI ≥ library date.”
- Fallback model `anthropic.claude-3-7-sonnet-20250219-v1:0` in AD-6 assumption — plausible AgentCore quickstart reference; not re-verified here.

No invented version numbers detected.

---

### 5. Ratifies rather than contradicts brownfield

**Pass.** Repo is greenfield scaffold; README is the only brownfield signal.

| README signal | Spine disposition | Assessment |
| --- | --- | --- |
| Layered path: React → Cognito → Stream Lambda → AgentCore → Gateway → APIs | Paradigm + diagram | Ratifies |
| Broader tool catalog (OpenFDA, UniProt, USPTO, …) | AD-3 exactly three; Deferred | Intentional V1 narrowing — matches PRD override |
| “Persistent research sessions” | AD-7 in-session only | Clarifies README ambiguity — good |
| `agents/framework/` in layout | Omitted from Structural Seed | Acceptable for V1 single-agent slice; **L-3** — note omission to avoid “missing folder” drift |
| Memory “AgentCore Memory / DynamoDB” | AD-7 picks AgentCore Memory | Resolves addendum option list — good |
| Six-domain agent taxonomy | AD-2 single agent synthesizes all | Scope honest for demoware |

No contradictions that would force a builder to fight the spine while following README for V1.

---

### 6. Covers driving PRD capabilities (FR-1..21, NFRs)

**Pass (coverage map); partial (explicit AD binding).**

#### Functional Requirements

| FR | Spine coverage | AD / location | Gap |
| --- | --- | --- | --- |
| FR-1 Sign in | Covered | AD-10 | — |
| FR-2 Manual provision | Covered | AD-10, AD-11 Outputs | — |
| FR-3 Start session / empty submit | Implicit | Capability map → `web/` | **M-1** — no rule |
| FR-4 Stream Event contract | Covered | AD-4, AD-5 | — |
| FR-5 Tool-use visibility | Covered | AD-4 (`tool_use`) | — |
| FR-6 Disclaimer | Covered | AD-14, map | Copy not in conventions (**L-4**) |
| FR-7 Sign out | Implicit | — | **M-1** |
| FR-8 Stream bridge only | Covered | AD-1 | Auth fork (**H-1**) |
| FR-9 Tool failure / session continues | Covered | AD-8 | — |
| FR-10 Multi-domain synthesis | Covered | AD-2, AD-6, AD-9, AD-14 | — |
| FR-11 Source Identifiers | Covered | AD-9 | Enforcement weak (**M-3**) |
| FR-12 Research-assist boundary | Partial | AD-14 prompt mention | **H-2** |
| FR-13 PubMed | Covered | AD-3 | — |
| FR-14 ClinicalTrials | Covered | AD-3 | — |
| FR-15 ChEMBL | Covered | AD-3 | — |
| FR-16 Exactly three tools | Covered | AD-3 | — |
| FR-17 Follow-up memory | Covered | AD-7 | — |
| FR-18 CDK deploy | Covered | AD-11, Stack, Environments | — |
| FR-19 CDK Outputs | Covered | AD-11, conventions | — |
| FR-20 CDK destroy | Covered | AD-11 | — |
| FR-21 Docs | Covered | Structural Seed `docs/` | — |

All 21 FRs are architecturally reachable; 3 lack sharp AD rules.

#### Non-Functional Requirements

| NFR | Spine coverage | Gap |
| --- | --- | --- |
| NFR-1 No browser→Runtime | AD-1 | Auth fork (**H-1**) |
| NFR-2 Cognito required | AD-10, AD-1 (partial) | — |
| NFR-3 Least privilege / no secrets in repo | AD-12 | — |
| NFR-4 HTTPS baseline | Stack (CloudFront) | **L-5** implicit only |
| NFR-5 First tool_use <30s Warm Path | — | **M-2** |
| NFR-6 1–3 min answer soft expectation | — | **M-2** |
| NFR-7 Not contractual SLA | — | **M-2** (could cite “demoware best-effort”) |
| NFR-8 Tool error stream | AD-8 | — |
| NFR-9 Stall timeout 5 min | AD-4 | — |
| NFR-10 Debug logs | AD-12, conventions | — |
| NFR-11 No audit export | Out of scope | OK |
| NFR-12 Destroy-when-idle | AD-11, AD-12, Environments | — |
| NFR-13 Single region deploy | AD-6, Environments, conventions | — |

Open Questions #1, #3, #4 resolved in spine (AD-5, AD-6, AD-12). #5 correctly remains roadmap.

#### Success Metrics

SM-1..SM-5 mapped via capability table and ADs. **M-4:** SM-7 (add-tool-in-a-day extensibility) not architecturally seeded — only implied by AD-3 deferral and `gateways/database/` layout; no “how to add tool #4” invariant.

---

### 7. Every dimension at initiative altitude decided, deferred, or open

| Dimension | Status | Location |
| --- | --- | --- |
| Deploy model (CDK, two stacks) | **Decided** | AD-11 |
| Region / single demo account | **Decided** | AD-6, Environments |
| Destroy / cost posture | **Decided** | AD-11, AD-12, Environments |
| Stream event contract | **Decided** | AD-4 |
| Model pin | **Decided** | AD-6 |
| Memory mechanism | **Decided** | AD-7 (AgentCore Memory) |
| Log retention | **Decided** | AD-12 (7 days) |
| Tool count | **Decided** | AD-3 |
| UI auth → Stream Lambda | **Open fork** | AD-1 OR — **H-1** |
| Stream Lambda runtime lang | **Assumption** | Open Assumptions #4 |
| React bundler | **Assumption** | Open Assumptions #3, Deferred |
| Reasoning events | **Assumption** | AD-5 |
| Performance demo bars | **Unlisted** | **M-2** |
| Tool timeout seconds | **Unlisted** | Medium — demoware can default in stories |
| Bedrock access failure UX | **Unlisted** | Medium — PRD UJ-2 edge |
| CORS / CloudFront→Stream origin | **Unlisted** | Low for single-origin patterns |
| Multi-env promotion | **Decided no** | Environments |

Operational envelope is sufficient for internal demoware; auth mechanism is the one initiative-level hole.

---

### 8. Stakes alignment (internal builder demoware)

**Pass.** Spine avoids enterprise theater (no WAF mandate, no SLA, no audit export, single region, 7-day logs, destroy-first ops). Deferred section is appropriately thin. Findings above are proportionate — not asking for platform teams or multi-region DR.

---

## Findings (by severity)

### High

**H-1 — AD-1 auth mechanism undecided (SigV4 Identity Pool vs JWT authorizer)**  
- **AD:** AD-1, Consistency Conventions (Auth header)  
- **Issue:** Adopted AD presents two preferred UI→Stream auth patterns. Web (Amplify/Cognito SDK creds) and infra (Function URL authorizer vs IAM) implementations diverge without violating the spine.  
- **Fix:** Pick one V1 pattern in AD-1 (recommend JWT authorizer on Function URL for simpler browser flow, or Identity Pool + SigV4 if matching README literally) and move the other to Deferred/Alternatives.

**H-2 — FR-12 research-assist boundary not rule-bound**  
- **AD:** AD-14  
- **Issue:** “Agent system prompt + UI Disclaimer” prevents divergence rhetorically but is not enforceable or testable at architecture level. PRD requires no dosing/clinical orders in demo answers.  
- **Fix:** Add AD rule: system/developer prompt must include research-only constraints; demo smoke includes one negative probe (e.g., dosing question → refusal framing). Bind FR-12 explicitly.

### Medium

**M-1 — FR-3 and FR-7 lack AD rules**  
- **AD:** (none)  
- **Issue:** Empty-message no-op and sign-out/session invalidation are real UI/stream forks.  
- **Fix:** Short AD or extend AD-10: empty submit does not call stream; sign-out clears client session and rejects stream until re-auth.

**M-2 — NFR-5/6/7 performance expectations unaddressed**  
- **AD:** (none)  
- **Issue:** PRD soft demo bars (<30s first `tool_use` Warm Path; 1–3 min typical turn) not decided, deferred, or open.  
- **Fix:** Add Open Assumption or Deferred note: “best-effort; smoke script logs timing, no CI gate.”

**M-3 — AD-9 Source Identifier rule is prompt-only**  
- **AD:** AD-9  
- **Issue:** “Must include” IDs when tools return them cannot be verified by infra; agent teams can diverge.  
- **Fix:** Specify citation block in stream (`token` tail or dedicated optional event) or smoke assertions on Herceptin PubMed turn.

**M-4 — SM-7 extensibility not architecturally seeded**  
- **AD:** AD-3 (negative scope only)  
- **Issue:** “Add tool in a day” has no pattern AD (gateway registration, IAM template, naming).  
- **Fix:** One paragraph in AD-3 or AD-11: new tool = new Lambda in `gateways/database/` + Gateway registration + no agent core rewrite.

**M-5 — Tool timeout / retry defaults undecided**  
- **AD:** AD-8  
- **Issue:** Error surface defined but not timeout values; three tool Lambdas may use different limits.  
- **Fix:** Convention row: e.g., 30s tool timeout, single retry on 429 for public APIs (align addendum §D).

**M-6 — Bedrock model access failure path not in spine**  
- **AD:** AD-6  
- **Issue:** PRD UJ-2 requires documented remediation when model access missing; AD-6 says “operator must enable” but not stream/deploy error shape.  
- **Fix:** Docs + deploy smoke note; optional `error` code for `ModelAccessDenied`.

### Low

**L-1 — AD-5 missing `[ADOPTED]` tag**  
- **AD:** AD-5  
- **Issue:** Inconsistent with AD-1–AD-4, AD-6–AD-14 tagging.  
- **Fix:** Add `[ADOPTED]` or `[ASSUMPTION]` consistently.

**L-2 — CDK CLI version not co-pinned with aws-cdk-lib 2.262**  
- **AD:** Stack  
- **Fix:** Note “CDK CLI latest 2.x, release date ≥ library” per AWS split cadence.

**L-3 — README `agents/framework/` omitted from Structural Seed**  
- **Fix:** Footnote “V1 excludes framework/; post-V1 agent shared libs.”

**L-4 — Approved Disclaimer copy not in Consistency Conventions**  
- **AD:** AD-14  
- **Fix:** Paste addendum §F verbatim into conventions table.

**L-5 — NFR-4 HTTPS-only implicit**  
- **Fix:** One line under Environments or AD-11: CloudFront HTTPS only, no HTTP redirect exception needed beyond CDK defaults.

---

## Recommended next actions (minimal)

1. **Resolve H-1** in AD-1 before parallel `web/` and `infra/backend` stories.  
2. **Add FR-12 binding** (H-2) — prompt invariant + demo negative probe.  
3. **Record M-2** as Open Assumption (“timing best-effort, smoke logs only”).  
4. Optional story-time: M-1, M-3, M-4, M-5, L-4.

---

## Summary

| Criterion | Result |
| --- | --- |
| Divergence points | Strong except auth (**H-1**) |
| AD enforceability | 11/14 fully enforceable; AD-1, AD-9, AD-14 partial |
| Deferred safety | Safe |
| Tech versions | Verified-current |
| Brownfield ratification | Ratifies README for V1 slice |
| FR/NFR coverage | All reachable; 3 FR + 3 NFR soft spots |
| Ops envelope | Adequate for demoware; auth fork open |
| Stakes fit | Lean, appropriate |

**Verdict: adequate** — ship epics after closing **H-1**; **H-2** and medium items can land in first stories without re-architecting.
