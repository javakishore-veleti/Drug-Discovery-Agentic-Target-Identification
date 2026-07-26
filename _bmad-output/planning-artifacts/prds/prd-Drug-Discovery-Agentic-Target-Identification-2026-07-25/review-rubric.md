# PRD Quality Review — Agentic Target ID

## Overall verdict

This PRD is well-calibrated for internal/builder demoware: it states an honest thesis (“deployable vertical slice—not a 30+ tool suite”), backs every FR with testable consequences, and pairs success metrics with counter-metrics. Scope omissions are explicit and indexed assumptions are mostly disciplined. The main risk before story creation is a handful of soft done-ness bars—observability, agent behavioral boundary, and stream-stall timeout—where the PRD defers specifics that NFR-9 already assumes will exist.

## Decision-readiness — strong

Trade-offs are stated plainly, not smoothed away. Vision §1 names what was given up (“not a 30+ tool suite and not a proprietary validated-target platform”) and what was chosen (“competes on AgentCore plumbing, governance shape… and time-to-pilot—not on a biology moat”). Non-Goals §5 and Non-Users §2.2 list deferrals with equal clarity (SSO, PHI, clinical-grade ranking, tools 4–5). Open Questions §11 are genuinely unresolved—model ID pin, `reasoning` event availability, log retention—not rhetorical prompts with answers buried elsewhere. UJ-2 honestly separates V1 from stretch (“post-V1 stretch metric; V1 docs must not block this path” for add-tool-in-a-day). No findings required at this stakes level.

## Substance over theater — strong

Content is earned, not template furniture. Two personas (Asha, Dev) each anchor a load-bearing UJ; neither exists for headcount. Differentiation is product-specific: “AgentCore plumbing, governance shape (browser never invokes AgentCore directly), and time-to-pilot.” NFRs carry demo thresholds, not boilerplate—NFR-5 “first `tool_use` visible in **<30 seconds** on Warm Path,” NFR-6 “full answer often completes in **1–3 minutes**,” NFR-7 explicitly “not contractual SLAs.” Vision cannot swap into an arbitrary life-sciences PRD without rewriting Herceptin/HER2, three Gateway Tools, and CDK destroy. No findings required.

## Strategic coherence — strong

The PRD has a clear thesis arc: AWS-native research copilot vertical slice optimized for shippable AgentCore demo, not biology moat. Features §4 follow that arc (auth → secure stream → agent → three tools → session memory → CDK lifecycle) rather than a disconnected backlog. Success Metrics §7 validate the thesis operationally—SM-1 time-to-demo, SM-2 exactly three tools, SM-4 source traceability, SM-5 clean teardown—and name counter-metrics that guard against scope creep (SM-C1 “Do not expand past 3 to ‘look complete’”; SM-C3 “Do not optimize for authoritative medical tone”). MVP §6.1/§6.2 scope kind (problem-solving vertical slice) matches the stated stakes in §0. No findings required.

## Done-ness clarity — adequate

FRs §4 are the strength of this PRD: each carries **Consequences (testable)** with verifiable conditions (e.g., FR-5 “at least one `tool_use` for PubMed is visible… before `done`”; FR-17 follow-up without restating “Herceptin”). Performance NFRs bound expectations (NFR-5/6). A few bars remain adjective-driven or deferred in ways that story authors must infer.

### Findings

- **medium** Stream-stall timeout undeclared (§11 Open Q #2 vs §8.3 NFR-9) — Open Question #2 asks to “pick during implementation” for “Concrete stream stall timeout shown in UI (e.g. 3 vs 5 minutes),” yet NFR-9 already assumes “client shows a terminal state within a documented timeout if the stream stalls.” *Fix:* Pick a default bound in the PRD (even a soft range) or move stall timeout from Open Questions to an explicit `[ASSUMPTION]` with a provisional value.*

- **medium** Observability bar is subjective (§8.4 NFR-10) — “Basic logs exist… sufficient to debug a failed demo (request/session id, tool name, error message)” names fields but leaves “sufficient” unbounded—no minimum log destinations, retention, or a smoke-test failure scenario. *Fix:* Add one concrete debug scenario (e.g., forced PubMed timeout) and the minimum log fields/locations an operator must find.*

- **low** Agent behavioral boundary is prompt-level only (§4.4 FR-12) — Consequences require “system/developer instructions” and that “demo answers do not instruct dosing,” but no acceptance probe defines pass/fail for the canonical Herceptin prompts beyond reviewer judgment. *Fix:* Add 1–2 negative test prompts or explicit “must not contain” patterns for the demo script.*

- **low** Error-event shape allows implementation drift (§4.3 FR-9) — “produces an `error` event (or `tool_result` + `error` as implemented)” gives two acceptable shapes without stating which the UI must handle for V1 acceptance. *Fix:* Pick one canonical failure surface for the demo acceptance path; note alternates in addendum only.*

## Scope honesty — strong

Omissions are explicit, not inferred. Non-Goals §5, per-feature **Out of Scope** (§4.1), and MVP Out of Scope §6.2 repeat deferrals (SSO, tools 4–5, cross-day resume, SLAs) so a reader cannot silently assume them in. Six inline `[ASSUMPTION]` tags are indexed at §12 Assumptions Index; Open Questions §11 count (five) is proportionate for a draft demoware PRD heading to build. SM-7 is honestly scoped as “measured post-V1.” No findings required.

## Downstream usability — adequate

The PRD declares chain-top intent (“for downstream UX, architecture, and epic/story work,” §0) and delivers usable extract surfaces: Glossary §3 anchors vocabulary; FR-1–FR-21, UJ-1–UJ-2, SM-1–SM-7 / SM-C1–C3, NFR-1–NFR-13 are contiguous and cross-linked (“Validates FR-…,” “Realizes UJ-…”). UJs §2.3 carry named protagonists (Asha, Dev) with inline context. `addendum.md` correctly holds mechanism notes (stream payload shapes, memory options) without polluting FRs.

### Findings

- **low** Assumption index roundtrip gaps (§12 Assumptions Index vs §4.1 FR-2, §4.4 FR-10) — Index lists “Manual Cognito user create via AWS CLI/console is acceptable UX” under §4.1 FR-2 and “Pathway / cardiotoxicity framing… without dedicated pathway/FAERS tools” under §4.4 FR-10, but neither FR body carries an inline `[ASSUMPTION]` tag. *Fix:* Add matching inline tags on those FRs or remove orphan index entries.*

## Shape fit — strong

Stakes §0 (“internal / builder demoware vertical slice”) match the document shape: capability spec plus two operational UJs (scientist demo, operator deploy/destroy), not enterprise rollout theater. UJ density (two) is appropriate for a forkable AWS sample with a named demo narrative. Brownfield alignment is honest—FR-8 and Assumptions Index reference README architecture without pretending greenfield. Consumer-product over-formalization (many personas, engagement DAU metrics) is absent. No findings required.

## Mechanical notes

- **Assumptions Index roundtrip:** Four inline `[ASSUMPTION]` tags in FR-4, FR-8, NFR-3, NFR-9 resolve cleanly in §12; Warm Path cold-start exclusion is indexed from §3 Glossary + §8.2. Two index-only entries (FR-2 operator UX, FR-10 pathway-without-FAERS) lack inline tags—see Downstream usability finding.
- **Glossary drift:** Minimal. “Chat Session,” “Stream Event,” “Gateway Tool,” and “Source Identifier” are used consistently across FRs, UJs, and SMs.
- **ID continuity:** FR-1–FR-21 sequential; UJ-1–UJ-2; SM / SM-C IDs unique; cross-references checked (e.g., SM-1 → FR-18, FR-19, FR-3–FR-5, FR-10) all resolve.
- **UJ protagonists:** UJ-1 (Asha), UJ-2 (Dev)—both named with persona + context inline.
- **Required sections for stakes:** Vision, user/journeys, glossary, FRs with consequences, non-goals, MVP scope, success metrics with counter-metrics, NFRs, constraints, dependencies, open questions, assumptions index—all present; no `[NOTE FOR PM]` callouts, but Open Questions §11 cover deferred decisions adequately for this stakes level.
