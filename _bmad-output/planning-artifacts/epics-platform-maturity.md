# Epics M: Platform maturity (post-V1 backlog)

**Status:** backlog (Fast-path BMAD) · **Date:** 2026-07-26  
**Binds:** `roadmap-platform-maturity.md` · PRD addendum §L · V1 PRD Non-Goals  
**V1 unchanged:** Epics 1–6 remain the only required cloud path. Do **not** start these stories until V1 SM-1…SM-5 stay green and you intentionally leave destroy-when-idle.

## Goal

Turn the deferred maturity catalog into BMAD epics/stories with testable ACs—so evals, observability, SRE, security hardening, HA/scale, events, and optional vector/RAG have a clear backlog without bloating the V1 PRD.

## Non-goals (still)

- Replacing V1 “destroy-when-not-demoing” as the default operating model in these epics’ first stories
- Multi-agent Runtime / specialist cloud deploy (still Epic L / addendum §K only)
- Expanding V1 Gateway tools beyond 3 inside Epic M1–M2 (tool growth is Epic M3, gated)

## Ladder → Epics

| Ladder | Epic | Focus |
| --- | --- | --- |
| V1.5 | **M1** | Agent evals + CloudWatch dashboards/alarms |
| V2 platform | **M2** | OTel, metrics, alerts, CloudTrail ops notes, spend alarms |
| V2 product | **M3** | Optional RAG/vector + tool growth gates |
| V3 ops | **M4** | Blue/green, SRE/SLOs, EventBridge/Kafka only if needed |
| Cross-cut | **M5** | Security hardening beyond V1 baseline |

---

## Epic M1: Agent evals + CloudWatch ops (V1.5)

Operator can run a golden-prompt eval smoke and see CloudWatch dashboards/alarms for stream/tool failures—without Grafana/ELK or on-call.

**PM-FRs:** PM-FR-1…PM-FR-4  
**Depends on:** Epics 1–6 complete (code exists even if stacks are destroyed)

### Story M1.1: Golden-prompt eval suite (local + optional cloud)

As a builder,  
I want a documented golden-prompt eval set for Herceptin MoA + cardiotoxicity + clinical-refusal,  
So that agent quality regressions are catchable without a full UI demo.

**Acceptance Criteria:**

**Given** the Unified Research Agent can run locally (and optionally against deployed Runtime)  
**When** I run the documented eval entrypoint  
**Then** at least three prompts execute: (1) Herceptin MoA, (2) cardiotoxicity follow-up or equivalent, (3) clinical-advice refusal probe  
**And** the harness records pass/fail for: research-assist boundary held, at least one tool_use when evidence is expected, PMID/NCT/ChEMBL surfaced when tools return ids  
**And** results write to a local report path under `docs/` or `_bmad-output/` (no secrets)  
**And** evals do not require Grafana, Kafka, or vector DB

### Story M1.2: FR-12 negative probes in eval harness

As a builder,  
I want explicit “do not give dosing / treatment orders” probes,  
So that FR-12 regressions fail the suite.

**Acceptance Criteria:**

**Given** Story M1.1 harness  
**When** a clinical-order style prompt runs  
**Then** the scored output fails if it issues actionable dosing/treatment instructions  
**And** pass requires research-assist / verify-primary-sources framing

### Story M1.3: CloudWatch dashboard for Stream + tools

As an operator,  
I want a single CloudWatch dashboard for stream errors, duration, and tool failures,  
So that a failed demo is diagnosable without ELK/Grafana.

**Acceptance Criteria:**

**Given** app stacks can be deployed  
**When** I open the documented dashboard (CDK-created or console JSON in repo)  
**Then** widgets cover Stream Lambda errors/duration and tool Lambda errors (at least pubmed)  
**And** docs link the dashboard from `docs/deploy.md` or `docs/ops.md`  
**And** no Grafana/ELK dependency

### Story M1.4: CloudWatch alarms (operator email/SNS)

As an operator,  
I want alarms on stream 5xx and sustained tool errors,  
So that I notice breakage when the stack is left up.

**Acceptance Criteria:**

**Given** Story M1.3 metrics exist  
**When** Stream 5xx or tool error rate crosses a documented threshold  
**Then** an SNS (or email) alarm fires  
**And** docs state alarms are optional while destroy-when-idle remains default  
**And** no paging/on-call rotation is required

---

## Epic M2: Deep observability + account audit notes (V2 platform)

Distributed traces and richer metrics exist; CloudTrail and spend guardrails are documented for the account.

**PM-FRs:** PM-FR-5…PM-FR-9

### Story M2.1: OpenTelemetry traces Stream → Runtime → tools

As a builder,  
I want OTel (or X-Ray equivalent) traces across Stream, Runtime, and Gateway tools,  
So that a slow/failed turn shows a single trace id.

**Acceptance Criteria:**

**Given** deployed V1 path  
**When** a chat turn runs  
**Then** a trace includes spans for Stream invoke, Runtime turn, and at least one tool call when tools run  
**And** `sessionId` / `requestId` are correlatable in logs and trace attributes  
**And** docs describe how to view traces in AWS

### Story M2.2: Custom metrics (latency, tool errors, tokens if available)

As an operator,  
I want metrics for turn latency, tool error count, and token usage when exposed,  
So that soft NFR bars can be measured.

**Acceptance Criteria:**

**Given** Stream/tool Lambdas  
**When** turns complete  
**Then** CloudWatch metrics (or EMF) emit turn duration and tool error counts  
**And** docs map metrics to NFR-5/NFR-6 as informational (still not SLAs)

### Story M2.3: Alert runbook (not on-call)

As an operator,  
I want a short alert→debug runbook,  
So that alarms from M1/M2 lead to known checks.

**Acceptance Criteria:**

**Given** alarms exist  
**When** I follow `docs/ops.md` (or equivalent)  
**Then** steps cover: check Stream logs, Runtime logs, tool 429/timeout, Bedrock throttling  
**And** runbook states no 24×7 obligation

### Story M2.4: CloudTrail enablement notes (account-level)

As an operator,  
I want docs for enabling CloudTrail in the AWS account,  
So that API audit exists without inventing a product audit-export FR.

**Acceptance Criteria:**

**Given** `docs/ops.md` (or security doc)  
**When** I follow CloudTrail steps  
**Then** management events are recorded for the account/region used by the app  
**And** docs clarify Trail is account ops, not an end-user feature (NFR-11 still holds unless a later epic opens audit export)

### Story M2.5: Bedrock / Lambda spend alarms

As an operator,  
I want cost anomaly or budget alarms for Bedrock and Lambda,  
So that a forgotten stack cannot silently burn budget.

**Acceptance Criteria:**

**Given** AWS Budgets or Cost Anomaly Detection can be configured  
**When** I follow documented setup  
**Then** a budget/alert exists for the pilot account or tagged resources  
**And** docs still recommend destroy-when-not-demoing as primary control

---

## Epic M3: Optional retrieval & tool growth (V2 product, gated)

Add vector/RAG or new Gateway tools only when a concrete corpus or evidence-gap justifies it.

**PM-FRs:** PM-FR-10…PM-FR-12  
**Gate:** Written decision note in architecture before implementation starts.

### Story M3.1: Retrieval need decision record

As a builder,  
I want a short ADR/decision: “no vector DB” vs “add RAG for corpus X”,  
So that we do not add OpenSearch/pgvector by fashion.

**Acceptance Criteria:**

**Given** V1 public-API tool path works  
**When** the decision record is written under `planning-artifacts/architecture/`  
**Then** it states corpus ownership, refresh, PII/PHI exclusion, and success metric  
**And** default remains **no vector DB** unless the record explicitly adopts one

### Story M3.2: Vector store spike (only if M3.1 adopts)

As a builder,  
I want a minimal RAG spike behind a feature flag or separate stack,  
So that private/internal corpus questions can be answered with citations.

**Acceptance Criteria:**

**Given** M3.1 adopts a vector store  
**When** the spike deploys  
**Then** ingest + query path exists for a sample non-PHI corpus  
**And** answers cite chunk/source ids  
**And** production chat can keep V1 tools without RAG if flag off  
**And** if M3.1 did not adopt, this story stays **blocked / cancelled**

### Story M3.3: Gateway tool #4 candidate spike

As a scientist,  
I want one additional governed Gateway tool (e.g. Open Targets–style or UniProt) behind the same error/`ids` contract,  
So that evidence gaps in V1 can close without a tool free-for-all.

**Acceptance Criteria:**

**Given** FR-16 history and addendum §H backlog  
**When** tool #4 is chosen and implemented  
**Then** it uses shared timeout/429/`status: error` contract  
**And** default deploy documents whether tool #4 is on or off  
**And** eval suite (M1) gains at least one prompt that exercises tool #4

---

## Epic M4: Release engineering, SRE, events (V3 ops)

Always-on operation gets progressive delivery, SLOs, and an event backbone only if async workloads exist.

**PM-FRs:** PM-FR-13…PM-FR-17

### Story M4.1: Staging environment + promote path

As a builder,  
I want a documented staging deploy distinct from demo destroy-loop,  
So that changes can be validated before “prod” account use.

**Acceptance Criteria:**

**Given** CDK app can take a stage context  
**When** I deploy `staging`  
**Then** stacks are namespaced/tagged separately from demo  
**And** docs describe promote → prod (or second account) without requiring blue/green yet

### Story M4.2: Blue/green or traffic-shift for Runtime/UI

As an operator,  
I want a blue/green (or CloudFront/Runtime alias shift) path,  
So that agent image/UI updates can roll forward/back.

**Acceptance Criteria:**

**Given** staging exists (M4.1)  
**When** I run the documented release procedure  
**Then** traffic can shift to a new Runtime revision and/or Frontend  
**And** rollback steps are documented  
**And** V1 destroy-when-idle remains valid for personal demo accounts

### Story M4.3: SLO definitions (informational → optional alert)

As an operator,  
I want written SLOs for availability and turn success once always-on,  
So that SRE is explicit rather than implied by soft NFRs.

**Acceptance Criteria:**

**Given** metrics from M2  
**When** SLO doc is published  
**Then** it defines at least: stream success rate, warm-path latency target, error-budget policy  
**And** it states SLOs apply only to always-on environments—not destroy-when-idle demos  
**And** on-call is still optional until a later staffing decision

### Story M4.4: Load / concurrency smoke

As a builder,  
I want a small authenticated load smoke against Stream URL,  
So that multi-user concurrency pain is visible before scale claims.

**Acceptance Criteria:**

**Given** a deployed staging stack and test users  
**When** the load script runs at a documented modest concurrency (e.g. 5–10)  
**Then** report captures error rate and latency percentiles  
**And** no multi-region claim is made from this story alone

### Story M4.5: EventBridge (default) before Kafka/MSK

As a builder,  
I want async integration via EventBridge only if a real fan-out use case exists,  
So that we do not introduce Kafka for chat SSE.

**Acceptance Criteria:**

**Given** a written use case (e.g. deploy notifications, async ingest) in architecture  
**When** EventBridge rules/targets are added  
**Then** chat request path remains Stream→Runtime (no Kafka on hot path)  
**And** Kafka/MSK is explicitly **out** unless a follow-on story adopts it with throughput justification

### Story M4.6: Kafka/MSK adoption gate (optional)

As a builder,  
I want Kafka/MSK only after EventBridge is insufficient,  
So that event streaming cost/complexity stays justified.

**Acceptance Criteria:**

**Given** EventBridge path proven or rejected with reasons  
**When** MSK/Kafka is proposed  
**Then** decision record includes consumers, retention, PII rules, and cost  
**And** without that record, story remains cancelled

---

## Epic M5: Security hardening (beyond V1 baseline)

Hardening for shared/multi-tenant use without rewriting V1 auth model until needed.

**PM-FRs:** PM-FR-18…PM-FR-22

### Story M5.1: Lightweight threat model

As a builder,  
I want a short STRIDE-style threat note for the V1 path,  
So that later controls map to identified risks.

**Acceptance Criteria:**

**Given** architecture spine  
**When** `docs/security.md` (or planning note) is added  
**Then** it covers spoofing (auth), elevation (IAM), info disclosure (logs/prompts), DoS (public APIs/Bedrock)  
**And** PHI remains out of scope

### Story M5.2: CloudFront WAF managed rules (optional)

As an operator,  
I want optional WAF on CloudFront,  
So that public UI abuse is reduced when the URL is shared.

**Acceptance Criteria:**

**Given** Frontend stack  
**When** WAF is enabled via context flag  
**Then** managed rule groups attach to the distribution  
**And** docs warn of cost and false positives  
**And** default for personal destroy-when-idle demos may remain off

### Story M5.3: Cognito federation / SSO spike

As an enterprise evaluator,  
I want a documented SAML/OIDC federation spike path,  
So that Federate/Midway-style SSO is not a surprise rewrite.

**Acceptance Criteria:**

**Given** Cognito User Pool  
**When** federation spike docs (+ optional CDK flag) exist  
**Then** a test IdP can sign in a user to the app  
**And** V1 email/password admin-provisioned path remains supported

### Story M5.4: Secrets Manager pattern for future API keys

As a builder,  
I want a Secrets Manager pattern for optional tool keys (e.g. USPTO),  
So that keys never enter git when tools beyond public APIs appear.

**Acceptance Criteria:**

**Given** a tool that needs a key  
**When** secret is referenced from Lambda env/IAM  
**Then** secret is not in repo; rotate steps documented  
**And** public V1 three tools still need no keys

### Story M5.5: HA / multi-AZ expectations doc (no false SLAs)

As an operator,  
I want honest HA language (managed multi-AZ vs product HA promise),  
So that latency/scalability claims stay aligned with PRD soft NFRs.

**Acceptance Criteria:**

**Given** AWS managed services in use  
**When** HA doc section ships  
**Then** it states what AWS provides vs what we do not promise (RPO/RTO, multi-region)  
**And** no hard availability SLA is published unless M4.3 SLOs are adopted for always-on

---

## Suggested order

1. **M1.1 → M1.2** (evals; highest product value)  
2. **M1.3 → M1.4** (CloudWatch)  
3. **M5.1** (cheap; informs later security)  
4. **M2.*** when stacks stay up more often  
5. **M3.1** before any vector work  
6. **M4.*** only for always-on / shared environments  
7. **M5.2–M5.4** when sharing the URL beyond yourself

## BMAD implementation artifacts

Backlog story files: `_bmad-output/implementation-artifacts/stories/M*.md`  
Sprint board: `sprint-status.yaml` (status `backlog`)  
Roadmap map: `roadmap-platform-maturity.md`
