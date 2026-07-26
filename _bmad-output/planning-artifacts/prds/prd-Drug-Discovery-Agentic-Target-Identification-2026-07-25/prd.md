---
title: "PRD: Agentic Target ID"
status: final
created: 2026-07-25
updated: 2026-07-26
---

# PRD: Agentic Target ID

*Working name: Agentic Target ID · Repo: Drug-Discovery-Agentic-Target-Identification*

## 0. Document Purpose

This PRD defines V1 requirements for **Agentic Target ID**, an AWS-native research copilot for early drug-discovery target identification. It is for the builder/PM (same operator), and for downstream UX, architecture, and epic/story work.

It builds on:

- Finalized product brief: `_bmad-output/planning-artifacts/briefs/brief-Drug-Discovery-Agentic-Target-Identification-2026-07-25/brief.md`
- Public positioning language from `README.md` (secondary)

Structure: Glossary-anchored vocabulary; features with globally numbered FRs and testable consequences; cross-cutting NFRs; assumptions tagged inline and indexed. Implementation mechanism notes that are not product requirements live in `addendum.md`.

Stakes: internal / builder demoware vertical slice — optimize for clarity and shippability, not enterprise completeness.

## 1. Vision

Agentic Target ID lets a scientist ask multi-domain target-identification questions in natural language and receive a streamed, evidence-grounded synthesis with visible tool use. A Unified Research Agent on Amazon Bedrock AgentCore plans calls through an MCP-style AgentCore Gateway to public biomedical APIs, then answers with source identifiers the scientist can spot-check.

V1 is a deployable vertical slice—not a 30+ tool suite and not a proprietary validated-target platform. After CDK deploy, an authenticated user can run a Herceptin / HER2-style research conversation (mechanism, cardiotoxicity / patient-risk framing, safer-targeting hypotheses) with streaming `tool_use` and answer tokens, multi-turn session memory for at least one follow-up, and clean stack destroy when the demo is done.

The product competes on AgentCore plumbing, governance shape (browser never invokes AgentCore directly), and time-to-pilot—not on a biology moat or clinical-grade ranking.

## 2. Target User

### 2.1 Jobs To Be Done

**Primary — Asha (computational biologist / drug-discovery scientist)**

- Functional: Explore a target or drug (demo: Herceptin / HER2) across literature, trials, and chemistry evidence without hand-stitching PubMed, ClinicalTrials.gov, and ChEMBL.
- Functional: See which tools ran and which source IDs (PMID, NCT, ChEMBL) back claims.
- Contextual: Desk research and hypothesis generation before experimental validation or pipeline go/no-go.
- Emotional: Trust that answers are research assistance with honest scope—not clinical advice or “validated target” theater.

**Secondary — Dev (builder / operator)**

- Functional: Deploy the full slice to their AWS account, demo it, tear it down, and add a new Gateway tool later without rewriting the platform.
- Contextual: Learn and own an end-to-end AgentCore + MCP pattern.
- Social: Show a credible, forkable AWS life-sciences research-agent slice with professional docs and honest claims.

### 2.2 Non-Users (v1)

- Clinicians making real-time treatment decisions
- Anyone uploading or querying PHI / patient records
- Pipeline decision authorities seeking automated go/no-go without human scientific review
- Teams requiring Federate / Midway SSO or enterprise IdP in V1
- Buyers expecting a proprietary knowledge graph or clinical-grade target ranking

### 2.3 Key User Journeys

- **UJ-1. Asha runs a Herceptin / HER2 target-ID session.**
  - **Persona + context:** Asha, computational biologist, needs a fast evidence pass on Herceptin mechanism and cardiotoxicity risk before a target-discussion meeting.
  - **Entry state:** Cognito user already created by admin; she opens the CloudFront UI unauthenticated.
  - **Path:** (1) Signs in with email/password. (2) Starts a new Chat Session; sees research-assist Disclaimer. (3) Asks: “What is the mechanism of action of Herceptin?” (4) Watches Stream Events: `session_started`, optional `reasoning`, `tool_use` / `tool_result` for PubMed (and others as needed), then `token` answer with PMIDs when available, then `done`. (5) Follow-up: “Which patient populations are most vulnerable to Herceptin cardiotoxicity?”—session memory uses prior context; ClinicalTrials and/or PubMed may run; NCT/PMID IDs surface when returned. (6) Signs out.
  - **Climax:** She sees tool activity live and can click or copy a PMID/NCT to spot-check a claim.
  - **Resolution:** Session ends on logout or browser close; no requirement to resume tomorrow from a session list.
  - **Edge case:** One tool times out → `error` Stream Event for that failure; conversation remains usable for another turn.

- **UJ-2. Dev deploys, demos, destroys, and extends.**
  - **Persona + context:** Dev owns the AWS account and wants a working vertical slice to demo and tear down cost-consciously.
  - **Entry state:** Prerequisites met (Bedrock model access, CDK bootstrap, CLI, Node, Python, Docker).
  - **Path:** (1) `cdk deploy` (or documented equivalent) succeeds; reads documented CDK Outputs (UI URL, Cognito pool/client IDs, stream endpoint). (2) Creates Cognito user via admin/CLI. (3) Completes UJ-1 demo in under 15 minutes after deploy. (4) `cdk destroy` removes app stacks cleanly. (5) Later: adds one new Gateway Tool in under a day using docs/patterns (post-V1 stretch metric; V1 docs must not block this path).
  - **Climax:** Live Herceptin demo with visible tool_use + streamed answer.
  - **Resolution:** Stacks gone or idle cost avoided; repo remains forkable.
  - **Edge case:** Missing Bedrock model access → deploy or first invoke fails with documented remediation, not a silent hang.

## 3. Glossary

- **Agentic Target ID** — This product; AWS-native research copilot for early drug-discovery target identification.
- **Unified Research Agent** — Single multi-domain agent on AgentCore Runtime that plans tool use and synthesizes answers for target-identification questions.
- **Chat Session** — One authenticated research conversation bounded to a browser/AgentCore session; holds multi-turn context for V1 (no cross-day resume UI).
- **Stream Lambda** — Authenticated backend streaming bridge between the UI and AgentCore Runtime (SSE). Browser never calls AgentCore invoke APIs directly.
- **Stream Event** — Typed SSE payload to the UI. V1 types: `session_started`, `reasoning`, `token`, `tool_use`, `tool_result`, `error`, `done`.
- **AgentCore Gateway** — MCP-style gateway that exposes Gateway Tools to the Unified Research Agent.
- **Gateway Tool** — One callable biomedical tool behind the Gateway. V1 set: PubMed, ClinicalTrials.gov, ChEMBL.
- **Source Identifier** — Traceable public ID returned by tools and surfaced in answers when available: **PMID**, **NCT ID**, **ChEMBL ID**.
- **Disclaimer** — Persistent UI research-assist notice (not medical advice; verify primary sources; not for clinical decision-making).
- **CDK Outputs** — Documented stack outputs required to operate the slice (at minimum: frontend URL, Cognito identifiers, stream endpoint).
- **Warm Path** — Demo path after stacks are deployed and the agent/runtime has been exercised at least once in the session window (excludes cold image pull as the success bar).

## 4. Features

### 4.1 Authentication (Cognito)

**Description:** Researchers and the builder access the chat UI only after Cognito email/password authentication. V1 uses manual admin user creation post-deploy—no self-signup UI. Realizes UJ-1, UJ-2.

**Functional Requirements:**

#### FR-1: Sign in with Cognito email/password

An authenticated user can sign in to the hosted UI with Cognito email and password. Realizes UJ-1.

**Consequences (testable):**
- Unauthenticated requests to start or continue a Chat Session are rejected.
- Valid Cognito credentials grant access to the chat UI.
- Invalid credentials show a clear auth error and do not open a Chat Session.

#### FR-2: Manual user provisioning (no self-signup UI)

An admin/operator can create a Cognito user after deploy using documented admin/CLI steps. Realizes UJ-2. `[ASSUMPTION: Manual Cognito user create via AWS CLI/console is acceptable UX for V1 operators.]`

**Consequences (testable):**
- Docs describe create-user steps using CDK Outputs (user pool / client).
- V1 UI does not offer public self-registration.

**Out of Scope:**
- Federate / Midway / enterprise SSO
- Password-reset UX polish beyond Cognito defaults needed to sign in

### 4.2 Research Chat UI and Streaming

**Description:** React chat UI hosted on S3 + CloudFront. User starts a Chat Session, sends messages, and receives Stream Events including optional reasoning, tool visibility, and answer tokens. Disclaimer is always visible in the research surface. Realizes UJ-1.

**Functional Requirements:**

#### FR-3: Start Chat Session and send message

An authenticated user can start a Chat Session and submit a natural-language research question. Realizes UJ-1.

**Consequences (testable):**
- Submitting a non-empty message begins a stream for that turn.
- Empty submit does not invoke the agent.

#### FR-4: Stream Event contract

The Stream Lambda emits Stream Events consumed by the UI. Realizes UJ-1.

**Consequences (testable):**
- V1 event types include: `session_started`, `reasoning`, `token`, `tool_use`, `tool_result`, `error`, `done`.
- `reasoning` is optional (emitted when the agent exposes plan/thinking text); UI renders it if present and does not fail if absent.
- `token` events carry answer text for progressive display.
- `tool_use` includes tool name (at least) so the UI can show which Gateway Tool is running.
- `tool_result` indicates tool completion (success or structured failure detail as available).
- `done` marks end of the turn’s stream.
- Unknown future event types do not crash the UI (`[ASSUMPTION: UI ignores unknown types with a console/debug log]`).

#### FR-5: Tool-use visibility

During a turn that calls tools, the user can see tool activity in the UI before or while the answer streams. Realizes UJ-1.

**Consequences (testable):**
- For a Herceptin mechanism question that hits PubMed, at least one `tool_use` for PubMed is visible in the UI before `done`.

#### FR-6: Research Disclaimer in UI

The chat surface displays the Disclaimer for every Chat Session. Realizes UJ-1.

**Consequences (testable):**
- Disclaimer text includes, at minimum: research assistance only; not medical advice; verify claims against primary sources (PMID / NCT / ChEMBL IDs); not for clinical decision-making.
- Disclaimer is visible without opening a separate legal page as the only placement.

#### FR-7: Sign out

An authenticated user can sign out and end UI access to Chat Sessions. Realizes UJ-1.

**Consequences (testable):**
- After sign-out, chat/stream actions require sign-in again.

### 4.3 Stream Lambda Contract (Secure Path)

**Description:** All agent invocation goes Browser → Cognito-authenticated UI → Stream Lambda (SSE) → AgentCore Runtime. This is a product security boundary, not an implementation preference. Realizes UJ-1; underpins NFR security.

**Functional Requirements:**

#### FR-8: Authenticated stream bridge only

Only the Stream Lambda (or equivalent documented backend stream path) may invoke AgentCore Runtime on behalf of the user. Realizes UJ-1.

**Consequences (testable):**
- Browser bundle and public docs do not instruct direct AgentCore Runtime invoke from the client.
- Unauthenticated stream requests are rejected.
- `[ASSUMPTION: Stream uses Cognito-authenticated access to a Lambda Function URL (or API) with SigV4/IAM as in README architecture]`

#### FR-9: Tool/agent failure streams as error without killing the session

When a Gateway Tool times out or errors, the stream surfaces an `error` Stream Event and the Chat Session remains usable for subsequent turns. Realizes UJ-1 edge case.

**Consequences (testable):**
- Simulated/forced tool failure produces an `error` event (or `tool_result` + `error` as implemented) before or instead of a successful synthesis for that tool.
- User can submit another message in the same Chat Session after the failed turn.

### 4.4 Unified Research Agent

**Description:** Python / Strands / Claude-on-Bedrock agent on AgentCore Runtime answers target-identification questions by planning Gateway Tool use and synthesizing results. V1 demo narrative centers on Herceptin / HER2. Realizes UJ-1.

**Functional Requirements:**

#### FR-10: Multi-domain synthesis from public tools

The Unified Research Agent can answer questions spanning mechanism, safety / patient-risk framing, and design hypotheses using only V1 Gateway Tools and model reasoning over their results. Realizes UJ-1. `[ASSUMPTION: Pathway / cardiotoxicity framing in V1 may be answered from PubMed + trials + ChEMBL + model synthesis without dedicated pathway/FAERS tools.]`

**Consequences (testable):**
- Canonical demo prompts (mechanism of Herceptin; cardiotoxicity / vulnerable populations; safer-targeting hypotheses) each complete a turn with a streamed answer (`token` + `done`).
- Agent does not require FAERS, USPTO, or proprietary corpora for V1 acceptance.

#### FR-11: Surface Source Identifiers when available

When tool results include PMID, NCT ID, or ChEMBL ID, the synthesized answer (or clearly associated UI citation area) surfaces those identifiers for spot-checking. Realizes UJ-1.

**Consequences (testable):**
- For a PubMed-backed turn, at least one PMID appears when the tool returned PMIDs.
- For a ClinicalTrials-backed turn, at least one NCT ID appears when the tool returned NCT IDs.
- For a ChEMBL-backed turn, at least one ChEMBL ID appears when the tool returned ChEMBL IDs.
- Absence of IDs from a tool result does not fail the turn; the answer may note limited identifiers.

#### FR-12: Research-assist behavioral boundary

The agent frames outputs as research assistance and does not present itself as clinical decision support. Realizes UJ-1; aligns with Disclaimer.

**Consequences (testable):**
- System/developer instructions (or equivalent) include research-only / not medical advice constraints.
- Demo answers do not instruct dosing or patient-specific treatment plans as actionable clinical orders.

### 4.5 Gateway Tools (PubMed, ClinicalTrials.gov, ChEMBL)

**Description:** AgentCore Gateway exposes exactly three V1 Gateway Tools calling public APIs. Realizes UJ-1; enables SM tool-count metric.

**Functional Requirements:**

#### FR-13: PubMed tool callable via Gateway

The Unified Research Agent can invoke PubMed through the Gateway and receive literature results including PMIDs when found. Realizes UJ-1.

**Consequences (testable):**
- Agent can complete a literature-oriented turn using PubMed.
- Successful results expose PMID values to the agent for FR-11.

#### FR-14: ClinicalTrials.gov tool callable via Gateway

The Unified Research Agent can invoke ClinicalTrials.gov through the Gateway and receive trial results including NCT IDs when found. Realizes UJ-1.

**Consequences (testable):**
- Agent can complete a trials-oriented turn using ClinicalTrials.gov.
- Successful results expose NCT IDs to the agent for FR-11.

#### FR-15: ChEMBL tool callable via Gateway

The Unified Research Agent can invoke ChEMBL through the Gateway and receive chemistry/bioactivity results including ChEMBL IDs when found. Realizes UJ-1.

**Consequences (testable):**
- Agent can complete a chemistry-oriented turn using ChEMBL.
- Successful results expose ChEMBL IDs to the agent for FR-11.

#### FR-16: Exactly three V1 tools

V1 ships exactly these three Gateway Tools; additional tools are deferred. Realizes UJ-2 extensibility narrative without expanding V1 scope.

**Consequences (testable):**
- Gateway configuration for the default deploy exposes PubMed, ClinicalTrials.gov, and ChEMBL.
- USPTO, OpenFDA, UniProt, pathway DBs, etc. are not required for V1 acceptance.

### 4.6 Session Memory

**Description:** Multi-turn context within one Chat Session / AgentCore session so a follow-up can refer to prior turns. No cross-day session list or resume UI in V1. Realizes UJ-1.

**Functional Requirements:**

#### FR-17: Follow-up uses prior turn context

Within the same Chat Session, a follow-up question can refer to entities or topics from the previous turn without restating everything. Realizes UJ-1.

**Consequences (testable):**
- After a Herceptin mechanism turn, a follow-up that says “which patients are most vulnerable to its cardiotoxicity?” is answered in Herceptin/HER2 context without requiring the drug name again.
- Memory is not required to survive logout, new browser profile, or next-day resume UI.

### 4.7 Deploy and Destroy (CDK)

**Description:** First-class lifecycle: deploy to the operator’s AWS account, document outputs, destroy cleanly. Realizes UJ-2.

**Functional Requirements:**

#### FR-18: CDK deploy of the V1 slice

An operator can deploy auth, stream, agent, gateway, and frontend hosting with CDK to `us-east-1` or the account default region with Bedrock model access. Realizes UJ-2.

**Consequences (testable):**
- Documented deploy command completes successfully on a prepared account.
- Required AWS building blocks are present: Bedrock + AgentCore Runtime, AgentCore Gateway (MCP), Cognito, Stream Lambda path, S3/CloudFront UI, CDK.

#### FR-19: Documented CDK Outputs

Deploy produces documented CDK Outputs sufficient to run the demo. Realizes UJ-2.

**Consequences (testable):**
- Docs list output keys/values needed for: frontend URL, Cognito user-pool/client identifiers, stream endpoint (and any other values required to create a user and chat).
- Operator can complete sign-in + one demo turn using only those outputs plus create-user steps.

#### FR-20: CDK destroy cleans app stacks

An operator can destroy deployed app stacks with CDK when not demoing. Realizes UJ-2.

**Consequences (testable):**
- Documented destroy command removes the application stacks created by deploy.
- Docs note any retained resources (e.g. CDK bootstrap, logs) if applicable—no silent surprise bill from leaving the full app up after “destroy.”

#### FR-21: Install / deploy / destroy documentation

Clear technical docs cover prerequisites, install, deploy, user create, demo smoke path, and destroy. Realizes UJ-2.

**Consequences (testable):**
- A new operator following docs alone can reach SM-1 (demo <15 minutes after deploy) without undocumented tribal steps.
- Docs use honest scope language (research assist; not clinical-grade / validated-target platform).

## 5. Non-Goals (Explicit)

- Federate / Midway / enterprise SSO
- USPTO patent tool (and USPTO API key flows) in V1
- FAERS / Athena / heavy safety data pipelines
- Multi-agent swarm / multi-agent orchestration in production
- Closed-access literature corpora or proprietary knowledge graph
- Clinical decision support, PHI ingestion, or EHR integration
- Clinical-grade target ranking or “enterprise validated target” product claims
- Heavy WAF / CI polish beyond what the vertical slice needs to be safely demoable
- Copying proprietary sample code from external AgentCore sample repos (patterns/architecture only)
- Cross-day session resume / session list UI
- Self-signup / public registration UI
- Shipping more than three Gateway Tools in V1
- Hard production SLAs or 24/7 on-call
- Separate AgentCore Runtimes / CDK stacks for domain specialist agents (local CLI suite only — see addendum §K)
- Full platform maturity stack in V1 (evals harness, OpenTelemetry, Grafana/ELK, CloudTrail-as-product, blue/green, Kafka/MSK, SRE on-call/SLOs, HA/latency SLAs, vector DB/RAG) — catalogued for later in `_bmad-output/planning-artifacts/roadmap-platform-maturity.md` (do not expand this PRD with those chapters)

## 6. MVP Scope

### 6.1 In Scope

- Cognito email/password auth; manual admin user create
- React chat UI (S3 + CloudFront) with Disclaimer and Stream Event rendering
- Stream Lambda → AgentCore Runtime (no browser→AgentCore direct invoke)
- Unified Research Agent (Python / Strands / Claude on Bedrock)
- AgentCore Gateway with exactly 3 tools: PubMed, ClinicalTrials.gov, ChEMBL
- Session memory for multi-turn within one Chat Session
- Source Identifier surfacing (PMID / NCT / ChEMBL) when tools return them
- Tool/agent failure via `error` Stream Event; session continues
- CDK deploy + destroy; documented CDK Outputs
- Herceptin / HER2 demo narrative
- Honest technical/professional docs and branding language

### 6.2 Out of Scope for MVP

- Tools 4–5 and broader README catalog (OpenFDA, UniProt, Reactome, USPTO, …) — deferred post-V1
- Open Targets–style structured target evidence and pathway tools — near-term after V1
- Multi-agent orchestration — after structured evidence tools
- Federate SSO, heavy WAF/CI, PHI, clinical systems

### 6.3 Local specialist suite (non-cloud; addendum §K)

Folder-parity specialist CLIs (drug profile, patient risk, pathway, cardioprotection, drug design, plus local supervisor stubs and genetic-risk package) may exist under `agents/` for local experimentation. They are **not** V1 cloud FRs, **not** required for SM-1, and **must not** be deployed as additional Runtimes in V1. Requirements and ACs: `addendum.md` §K; stories: `epics-local-specialists.md`.

## 7. Success Metrics

**Primary**

- **SM-1**: Time-to-demo — After successful CDK deploy, operator completes login + Herceptin-style question with visible `tool_use` + streamed answer in **<15 minutes**. Validates FR-18, FR-19, FR-3–FR-5, FR-10.
- **SM-2**: Tool coverage — **Exactly 3** Gateway Tools callable in the default deploy (PubMed, ClinicalTrials.gov, ChEMBL). Validates FR-13–FR-16.
- **SM-3**: Multi-turn memory — One follow-up in the same Chat Session correctly uses prior context (Herceptin/HER2 continuity). Validates FR-17.
- **SM-4**: Source traceability — Demo answers surface PMID and/or NCT and/or ChEMBL IDs when corresponding tools return them, enough to spot-check claims. Validates FR-11.
- **SM-5**: Clean teardown — Documented `cdk destroy` removes app stacks so the demo environment is not left fully running. Validates FR-20.

**Secondary**

- **SM-6**: Docs completeness — Install / deploy / destroy / create-user / smoke demo path documented. Validates FR-21.
- **SM-7**: Extensibility readiness — Docs/patterns support adding one new Gateway Tool in under a day (measured post-V1; V1 must not architecturally preclude it). Related to UJ-2.

**Counter-metrics (do not optimize)**

- **SM-C1**: Number of Gateway Tools in V1 — Do not expand past 3 to “look complete”; counterbalances SM-2.
- **SM-C2**: Answer length / tool-call count — Do not maximize verbosity or tool thrash; counterbalances SM-1 latency comfort.
- **SM-C3**: Clinical-sounding confidence — Do not optimize for authoritative medical tone; counterbalances SM-4 trust via citations.

## 8. Cross-Cutting NFRs

### 8.1 Security

- **NFR-1:** No browser→AgentCore Runtime direct invoke; Stream Lambda (authenticated) is mandatory. Validates FR-8.
- **NFR-2:** Cognito required for chat/stream access. Validates FR-1.
- **NFR-3:** Secrets, API keys, and AWS credentials are not committed to the repo; gateway/agent roles follow least privilege as documented. `[ASSUMPTION: V1 public tools need no long-lived third-party API keys; if rate-limit keys are added later, they stay in secrets manager / env—not git]`
- **NFR-4:** Heavy WAF is out of scope; baseline HTTPS via CloudFront and Cognito auth are required.

### 8.2 Performance (demo expectations, not SLA)

- **NFR-5:** Soft expectation — first `tool_use` visible in **<30 seconds** on Warm Path.
- **NFR-6:** Soft expectation — full answer often completes in **1–3 minutes** depending on tools/model; slower turns are acceptable for V1 demos if progress Stream Events continue.
- **NFR-7:** These are best-effort demo expectations, not contractual SLAs; no paging/on-call obligation.

### 8.3 Reliability / failure behavior

- **NFR-8:** Tool timeout or tool error yields a streamed `error` (and/or failed `tool_result`) and does not require redeploy to continue chatting. Validates FR-9.
- **NFR-9:** Partial tool success may still produce an answer that notes gaps; total agent failure still ends with `error` and/or `done` so the UI does not spin forever. Soft UI default: if the stream stalls with no terminal event, the client shows a terminal error/timeout state within **5 minutes** (best-effort demo UX, not an SLA).

### 8.4 Observability

- **NFR-10:** Basic logs exist for Stream Lambda and agent/tool invocations sufficient to debug a failed demo (request/session id, tool name, error message). No full observability platform required in V1.
- **NFR-11:** No requirement for end-user-facing audit export in V1.

### 8.5 Cost

- **NFR-12:** Destroy-when-not-demoing is the default operating model; docs emphasize teardown.
- **NFR-13:** No hard launch deadline; cost-conscious region single-deploy is enough.

## 9. Constraints and Guardrails

### 9.1 Platform and AWS must-use

- Bedrock + AgentCore Runtime
- AgentCore Gateway (MCP)
- Cognito
- Lambda stream path
- CDK
- S3 / CloudFront for UI
- Region: `us-east-1` or account default; Bedrock model access required

### 9.2 Data and safety

- Public biomedical APIs only
- No real patient / PHI data in V1
- Research assistance only; human scientific review required for any pipeline use
- Do not claim clinical-grade ranking, proprietary KG, closed literature corpus, or replacement for experimental validation

### 9.3 IP / sourcing

- Do not copy proprietary sample code from external AgentCore samples; use patterns/architecture only
- Public positioning may describe an agentic drug-discovery platform for target identification while remaining honest about V1 slice scope in docs

### 9.4 Form factor

- V1 surface: web (React) only

## 10. Integration and Dependencies

- **Amazon Bedrock** model access (Claude) in the deploy region
- **PubMed (NCBI)** public API — PMID identifiers; subject to public rate limits
- **ClinicalTrials.gov** public API — NCT IDs; subject to public rate limits / backoff
- **ChEMBL** public API — ChEMBL IDs; subject to public rate limits
- Operator workstation: AWS CLI, Node.js 22+, Python 3.12+, Docker, CDK bootstrap

## 11. Open Questions

*Resolved at finalize where noted. Remaining items are non-blocking for UX/architecture/epics.*

1. Exact Claude / Bedrock model ID pin vs “latest approved in account” — **deferred to architecture.**
2. Concrete stream stall timeout shown in UI — **resolved:** soft default **5 minutes** (see NFR-9).
3. Whether `reasoning` events are emitted by the chosen AgentCore/Strands streaming surface in V1 or remain optional-only — **deferred to architecture** (UI already tolerates absence per FR-4).
4. Minimum IAM/CloudWatch log retention days for cost vs debuggability — **deferred to architecture** (default account retention acceptable unless architecture chooses otherwise).
5. Preferred post-V1 tool #4 (Open Targets–style vs UniProt/Reactome) — **deferred to roadmap / architecture** (not V1).

## 12. Assumptions Index

*All accepted at finalize (2026-07-25).*

- `[ASSUMPTION]` UI ignores unknown Stream Event types without crashing (§4.2 FR-4). **Accepted.**
- `[ASSUMPTION]` Stream path uses Cognito-authenticated Lambda Function URL (or API) with SigV4/IAM per README (§4.3 FR-8). **Accepted.**
- `[ASSUMPTION]` V1 public tools need no committed third-party API keys (§8.1 NFR-3). **Accepted.**
- Soft UI stream-stall terminal state within **5 minutes** (§8.3 NFR-9) — promoted from assumption to NFR at finalize.
- `[ASSUMPTION]` “Warm Path” excludes first-ever cold container pull from the <30s first-`tool_use` soft bar (§3 Glossary, §8.2). **Accepted.**
- `[ASSUMPTION]` Manual Cognito user create via AWS CLI/console is acceptable UX for V1 operators (§4.1 FR-2). **Accepted.**
- `[ASSUMPTION]` Pathway / cardiotoxicity framing in V1 may be answered from PubMed + trials + ChEMBL + model synthesis without dedicated pathway/FAERS tools (§4.4 FR-10). **Accepted.**
