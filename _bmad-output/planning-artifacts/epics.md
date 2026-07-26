---
stepsCompleted: [step-01-validate-prerequisites, step-02-design-epics, step-03-create-stories, step-04-final-validation]
workflowStatus: complete
inputDocuments:
  - _bmad-output/planning-artifacts/briefs/brief-Drug-Discovery-Agentic-Target-Identification-2026-07-25/brief.md
  - _bmad-output/planning-artifacts/prds/prd-Drug-Discovery-Agentic-Target-Identification-2026-07-25/prd.md
  - _bmad-output/planning-artifacts/prds/prd-Drug-Discovery-Agentic-Target-Identification-2026-07-25/addendum.md
  - _bmad-output/planning-artifacts/architecture/architecture-Drug-Discovery-Agentic-Target-Identification-2026-07-25/ARCHITECTURE-SPINE.md
  - README.md
excludedDocuments:
  - UX design contract (none; skipped by owner)
  - architecture reviews/ (excluded unless conflict)
---

# Drug-Discovery-Agentic-Target-Identification - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for Agentic Target ID (Drug-Discovery-Agentic-Target-Identification), decomposing the requirements from the PRD, Architecture spine, brief, and README (secondary positioning/demo prompts only) into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: Sign in with Cognito email/password; unauthenticated chat/stream rejected.
FR2: Manual Cognito user provisioning post-deploy (admin/CLI); no self-signup UI in V1.
FR3: Authenticated user can start a Chat Session and submit a non-empty natural-language message.
FR4: Stream Lambda emits Stream Events: `session_started` | `reasoning` | `token` | `tool_use` | `tool_result` | `error` | `done`; UI tolerates missing `reasoning` and unknown types.
FR5: Tool-use visibility — for tool-calling turns (e.g. PubMed), at least one `tool_use` visible before `done`.
FR6: Research Disclaimer visible on chat surface (approved copy: research assistance only; not medical advice; verify PMID/NCT/ChEMBL; not for clinical decision-making).
FR7: User can sign out; subsequent chat/stream requires sign-in.
FR8: Only authenticated Stream Lambda path invokes AgentCore Runtime; no browser→AgentCore direct invoke.
FR9: Tool timeout/error streams `error` (and failed `tool_result`); Chat Session remains usable for next turn.
FR10: Unified Research Agent synthesizes multi-domain answers (mechanism, safety/patient-risk framing, design hypotheses) using only V1 Gateway Tools + model; Herceptin/HER2 demo completes with `token` + `done`.
FR11: Surface Source Identifiers (PMID / NCT / ChEMBL) in answers when tools return them.
FR12: Research-assist behavioral boundary — agent framed as research assistance, not clinical decision support; no actionable dosing/treatment orders.
FR13: PubMed tool callable via Gateway; exposes PMIDs when found.
FR14: ClinicalTrials.gov tool callable via Gateway; exposes NCT IDs when found.
FR15: ChEMBL tool callable via Gateway; exposes ChEMBL IDs when found.
FR16: Exactly three V1 Gateway Tools in default deploy (`pubmed`, `clinicaltrials`, `chembl`).
FR17: Follow-up in same Chat Session uses prior turn context (Herceptin continuity without restating drug name).
FR18: CDK deploy of V1 slice (auth, stream, agent, gateway, frontend) to `us-east-1` or account default with Bedrock model access.
FR19: Documented CDK Outputs sufficient to operate demo (FrontendUrl, Cognito ids, StreamUrl, etc.).
FR20: CDK destroy removes app stacks cleanly; docs note retained resources.
FR21: Install / deploy / destroy / create-user / smoke-demo documentation with honest scope language.

### NonFunctional Requirements

NFR1: No browser→AgentCore Runtime direct invoke; Stream Lambda mandatory (security).
NFR2: Cognito required for chat/stream access.
NFR3: No secrets/API keys/AWS credentials in git; least-privilege IAM for agent/gateway roles.
NFR4: Baseline HTTPS via CloudFront + Cognito; heavy WAF out of scope.
NFR5: Soft demo latency — first `tool_use` visible <30s on Warm Path (not SLA).
NFR6: Soft demo latency — full answer often 1–3 minutes; progress events acceptable (not SLA).
NFR7: Latency expectations are best-effort; no paging/on-call.
NFR8: Tool timeout/error yields streamed error path; no redeploy required to continue chatting.
NFR9: Partial success OK; stream must reach terminal UI state within soft **5 minutes** if stalled.
NFR10: Basic structured logs (sessionId, requestId, tool, error) for Stream Lambda and agent/tool invocations.
NFR11: No end-user audit export in V1.
NFR12: Destroy-when-not-demoing operating model; docs emphasize teardown.
NFR13: Cost-conscious single-region deploy; no hard launch deadline.

### Additional Requirements

From Architecture spine (AD-1..AD-15) and conventions — bind stories:

- AD-1: UI→Stream = Cognito User Pool → Identity Pool → SigV4 to IAM-auth Function URL; never Runtime IAM in browser.
- AD-2: Single Unified Research Agent (Strands + Claude); no multi-agent swarm.
- AD-3: Exactly three MCP tools named `pubmed`, `clinicaltrials`, `chembl` as Lambda Gateway targets.
- AD-4: Stream Event contract + `done` only after Runtime turn stream closes.
- AD-5: Emit `reasoning` only if runtime exposes thinking; never fabricate.
- AD-6: Pin model `us.anthropic.claude-sonnet-4-20250514-v1:0`; region default `us-east-1`; fallback to Claude 3.7 Sonnet if blocked.
- AD-7: Stream Lambda owns `sessionId`; AgentCore Memory for in-session multi-turn only.
- AD-8: On tool failure: `tool_result` status=error then `error` event; session continues.
- AD-9: `tool_result` includes top-level `ids: { pmid[], nct[], chembl[] }`; agent reads `ids` only.
- AD-10: Cognito email/password; admin-provisioned users.
- AD-11: CDK TypeScript Backend + Frontend stacks; Outputs: FrontendUrl, UserPoolId, UserPoolClientId, IdentityPoolId, StreamUrl.
- AD-12: Least-privilege IAM; CloudWatch Logs retention **7 days**.
- AD-13: Dependency direction — web↛agent Python; tools↛UI; app↛CDK imports.
- AD-14: Public APIs only; Disclaimer + agent prompt research-assist boundary.
- AD-15: Tool 429 backoff; per-tool timeout ≤45s → error path.
- Stack seed: aws-cdk-lib ^2.262, Node 22, Python 3.12, strands-agents ^1.47, Vite+React 18+, Docker agent image.
- Structural seed dirs: `agents/unified-research-agent/`, `gateways/database/`, `infra/backend|frontend/`, `web/`, `docs/`.
- Env names: `BEDROCK_MODEL_ID`, `AWS_REGION`, `AGENTCORE_GATEWAY_URL`, `AGENTCORE_MEMORY_ID`.
- No greenfield starter template beyond README layout — Epic 1 scaffolds repo from structural seed.
- Hands-on build phasing (owner): (1) local agent + PubMed, (2) gateway + 3 tools, (3) AgentCore Runtime, (4) Stream Lambda + SigV4, (5) Cognito + React UI, (6) CDK deploy/destroy + docs.
- README secondary only: Herceptin demo prompts + public positioning; do **not** expand V1 tool catalog from README.
- PRD addendum: approved Disclaimer copy; canonical demo prompts; public API rate-limit constraints (AD-15).

### UX Design Requirements

None — UX design contract excluded / not produced for V1 (thin chat UI).

### FR Coverage Map

FR1: Epic 5 — Cognito email/password sign-in
FR2: Epic 5 — Manual admin user provisioning (docs + pool)
FR3: Epic 5 — Start Chat Session and send message
FR4: Epic 4 — Stream Event contract (SSE types)
FR5: Epic 4 / Epic 5 — Tool-use visibility in stream and UI
FR6: Epic 5 — Research Disclaimer in chat UI
FR7: Epic 5 — Sign out
FR8: Epic 4 — Secure Stream Lambda bridge only
FR9: Epic 2 (tool error shape) / Epic 4 (stream error path)
FR10: Epic 1 (local synthesis) → Epic 3 (Runtime complete)
FR11: Epic 1 (PMID) → Epic 2 (PMID/NCT/ChEMBL ids)
FR12: Epic 1 / Epic 3 — Research-assist agent boundary
FR13: Epic 1 (local PubMed) → Epic 2 (Gateway PubMed)
FR14: Epic 2 — ClinicalTrials.gov Gateway tool
FR15: Epic 2 — ChEMBL Gateway tool
FR16: Epic 2 — Exactly three V1 tools
FR17: Epic 3 (Memory) → Epic 5 (E2E follow-up)
FR18: Epic 6 — CDK deploy
FR19: Epic 6 — Documented CDK Outputs
FR20: Epic 6 — CDK destroy
FR21: Epic 6 — Install/deploy/destroy/smoke docs

## Epic List

### Epic 1: Local literature research loop
Builder/scientist can run a Herceptin-style question locally against a Strands agent + PubMed and see PMIDs in the answer.
**FRs covered:** FR10 (partial), FR11 (PMID), FR12, FR13
**ADs:** AD-2, AD-6, AD-9, AD-14
**Phase:** (1) local agent + PubMed tool

### Epic 2: Governed three-tool evidence gateway
Agent can call PubMed, ClinicalTrials.gov, and ChEMBL through AgentCore Gateway with normalized `ids`, timeouts/429 handling, and error-shaped results.
**FRs covered:** FR9 (tool path), FR11, FR13–FR16
**ADs:** AD-3, AD-8, AD-9, AD-15
**Phase:** (2) gateway + 3 tools

### Epic 3: AgentCore Runtime + session memory
Unified Research Agent runs on AgentCore Runtime with pinned model and in-session multi-turn memory.
**FRs covered:** FR10, FR12, FR17
**ADs:** AD-2, AD-6, AD-7 (Memory), AD-14
**Phase:** (3) AgentCore Runtime

### Epic 4: Secure streaming research turns
SSE Stream Events via Stream Lambda; Runtime never invoked from the browser; tool failures stream `error` and session continues.
**FRs covered:** FR4, FR5, FR8, FR9
**ADs:** AD-1, AD-4, AD-5, AD-7 (`sessionId`), AD-8, AD-12
**NFRs:** NFR1, NFR8, NFR9, NFR10
**Phase:** (4) Stream Lambda + SigV4

### Epic 5: Authenticated research chat
Asha signs in (Cognito), chats with Disclaimer + live tool_use/answer stream (SigV4), follow-up works, signs out.
**FRs covered:** FR1–FR7, FR5, FR17 (E2E)
**ADs:** AD-1, AD-10, AD-14
**NFRs:** NFR2, NFR4
**Phase:** (5) Cognito + React UI

### Epic 6: Deployable pilot lifecycle
Dev CDK-deploys the slice, uses documented Outputs, runs smoke demo, destroys cleanly.
**FRs covered:** FR18–FR21
**ADs:** AD-11, AD-12, AD-13
**NFRs:** NFR3, NFR12, NFR13
**Phase:** (6) CDK deploy/destroy + docs

## Epic 1: Local literature research loop

Builder/scientist can run a Herceptin-style question locally against a Strands agent + PubMed and see PMIDs in the answer.

**FRs covered:** FR10 (partial), FR11 (PMID), FR12, FR13  
**ADs:** AD-2, AD-6, AD-9, AD-14

### Story 1.1: Scaffold agent package + pinned Bedrock model

As a builder,
I want a runnable `agents/unified-research-agent/` package with pinned `BEDROCK_MODEL_ID` and clear run instructions,
So that local agent work starts from the architecture stack with a known entrypoint.

**Acceptance Criteria:**

**Given** Python 3.12 and Bedrock model access in the target account/region  
**When** I follow `agents/unified-research-agent/` README to install (`requirements.txt` or equivalent) and run the documented entrypoint with a trivial prompt  
**Then** the agent invokes Bedrock using model id `us.anthropic.claude-sonnet-4-20250514-v1:0` (or the documented AD-6 fallback if pinned model is unavailable)  
**And** the model id is read from env/config (`BEDROCK_MODEL_ID`), not hardcoded only in scattered source  
**And** the package includes at least: package layout under `agents/unified-research-agent/`, dependency file, and README run instructions  
**And** no AgentCore Gateway, Stream Lambda, Cognito, or React UI is required for this story

### Story 1.2: Research-assist system prompt

As a scientist,
I want the agent constrained to research assistance,
So that answers are not framed as clinical advice (FR12, AD-14).

**Acceptance Criteria:**

**Given** the agent from Story 1.1  
**When** I ask a clinical-sounding dosing or patient-treatment question  
**Then** the reply refuses actionable clinical orders and states research-assistance / not medical advice boundaries  
**And** the system/developer prompt includes constraints equivalent to the approved Disclaimer (research only; verify primary sources; not for clinical decision-making)

### Story 1.3: Local PubMed tool with `ids.pmid`

As a scientist,
I want the agent to call a local PubMed tool that returns PMIDs in a normalized `ids` object,
So that literature answers are spot-checkable (FR13, FR11, AD-9).

**Acceptance Criteria:**

**Given** PubMed/NCBI is reachable from the local environment  
**When** the agent runs a literature query suitable for Herceptin/mechanism research  
**Then** the PubMed tool is invoked  
**And** a successful tool result includes top-level `ids.pmid` as a string array (empty array allowed if none found)  
**And** on HTTP 429 the tool backs off/retries per AD-15 intent, and on timeout or unrecoverable error within ≤45s wall clock returns an error-shaped result (does not hang indefinitely)

### Story 1.4: Local Herceptin synthesis with PMID surfacing

As a scientist,
I want a local answer that cites PMIDs when PubMed returns them,
So that I can spot-check claims before any cloud deploy (FR10, FR11).

**Acceptance Criteria:**

**Given** Stories 1.1–1.3 are complete  
**When** I ask “What is the mechanism of action of Herceptin?” via the local entrypoint  
**Then** the agent uses the PubMed tool and returns a synthesized answer  
**And** at least one PMID appears in the answer (or clearly associated citation output) when the tool returned PMIDs  
**And** the run completes without requiring Gateway, AgentCore Runtime, Stream Lambda, Cognito, or the React UI

## Epic 2: Governed three-tool evidence gateway

Agent can call PubMed, ClinicalTrials.gov, and ChEMBL through AgentCore Gateway with normalized `ids`, timeouts/429 handling, and error-shaped results.

**FRs covered:** FR9 (tool path), FR11, FR13–FR16  
**ADs:** AD-3, AD-8, AD-9, AD-15

### Story 2.1: Gateway scaffold + PubMed as MCP Lambda target

As a builder,
I want PubMed exposed through AgentCore Gateway as MCP tool `pubmed`,
So that the agent calls literature via the governed path (not only the local Epic 1 tool).

**Acceptance Criteria:**

**Given** AgentCore Gateway can be configured in the target account and Epic 1 PubMed behavior exists  
**When** the agent lists and calls the Gateway tool `pubmed`  
**Then** the tool executes against PubMed and a successful result includes top-level `ids.pmid` as a string array  
**And** the MCP tool name is exactly `pubmed` (AD-3)  
**And** PubMed adapter logic is shared with (or extracted from) the Epic 1 local tool so `ids.pmid` and timeout/429 behavior stay one implementation  
**And** tool code lives under `gateways/database/` (or documented equivalent) per structural seed

### Story 2.2: ClinicalTrials.gov Gateway tool `clinicaltrials`

As a scientist,
I want trial search via Gateway tool `clinicaltrials` with NCT IDs,
So that patient-risk / trial context is evidence-backed (FR14).

**Acceptance Criteria:**

**Given** Gateway from Story 2.1 is available  
**When** the agent calls `clinicaltrials` with a Herceptin/HER2-relevant query  
**Then** a successful result includes top-level `ids.nct` as a string array (empty allowed if none)  
**And** NCT values match `NCT` + 8 digits when present  
**And** on HTTP 429 the tool backs off/retries, and on timeout or unrecoverable error within ≤45s wall clock returns `tool_result` with `status: error` (AD-15)

### Story 2.3: ChEMBL Gateway tool `chembl`

As a scientist,
I want chemistry/bioactivity lookup via Gateway tool `chembl`,
So that design/chemistry claims can cite ChEMBL IDs (FR15).

**Acceptance Criteria:**

**Given** Gateway from Story 2.1 is available  
**When** the agent calls `chembl` with a Herceptin/HER2-relevant chemistry query  
**Then** a successful result includes top-level `ids.chembl` as a string array (empty allowed if none)  
**And** on HTTP 429 / timeout / unrecoverable error the same AD-15 resilience rules as Story 2.2 apply (`status: error` within ≤45s)

### Story 2.4: Enforce exactly three V1 tools + shared error contract

As a builder,
I want the default Gateway configuration to expose only the three V1 tools with a shared failure shape,
So that V1 scope stays honest and tool failures are consistent for streaming later (FR16, FR9, AD-8).

**Acceptance Criteria:**

**Given** the default V1 Gateway configuration  
**When** available MCP tools are listed  
**Then** only `pubmed`, `clinicaltrials`, and `chembl` are exposed  
**And** a forced/simulated tool failure returns `status: error` plus tool name and a short safe message (no secrets/stack traces)  
**And** after a failed tool call in a test session, the agent can accept another prompt/turn without redeploy

## Epic 3: AgentCore Runtime + session memory

Unified Research Agent runs on AgentCore Runtime with pinned model and in-session multi-turn memory.

**FRs covered:** FR10, FR12, FR17  
**ADs:** AD-2, AD-6, AD-7 (Memory), AD-14

### Story 3.1: Containerize agent for AgentCore Runtime

As a builder,
I want the Unified Research Agent packaged as a Runtime-deployable container with pinned model config,
So that cloud execution matches the local agent (AD-2, AD-6).

**Acceptance Criteria:**

**Given** Epic 1–2 agent and Gateway tool integration exist  
**When** I build the Docker image and deploy/register the AgentCore Runtime  
**Then** the Runtime uses `BEDROCK_MODEL_ID` set to the pinned model `us.anthropic.claude-sonnet-4-20250514-v1:0` (or documented AD-6 fallback)  
**And** there is a single Unified Research Agent entrypoint (no multi-agent swarm)  
**And** the Runtime is configured to reach the AgentCore Gateway tools from Epic 2  
**And** packaging lives under `agents/unified-research-agent/` per structural seed

### Story 3.2: Wire AgentCore Memory for Chat Session turns

As a scientist,
I want multi-turn context stored in AgentCore Memory for one session,
So that follow-ups do not require restating prior context (FR17, AD-7).

**Acceptance Criteria:**

**Given** Runtime from Story 3.1  
**When** two turns run with the same session key against Runtime  
**Then** Memory retains prior turn context for the second turn  
**And** configuration uses env name `AGENTCORE_MEMORY_ID` (no `MEMORY_ID` alias)  
**And** no session-list or cross-day resume UI is implemented

### Story 3.3: Herceptin multi-turn Runtime smoke (mechanism → cardiotoxicity)

As a scientist,
I want a Runtime smoke that answers mechanism then a cardiotoxicity follow-up without restating Herceptin,
So that FR10 and FR17 are proven on AgentCore with research-assist boundaries.

**Acceptance Criteria:**

**Given** Stories 3.1–3.2 and Gateway tools from Epic 2  
**When** turn 1 asks “What is the mechanism of action of Herceptin?” and turn 2 asks “Which patient populations are most vulnerable to its cardiotoxicity?”  
**Then** turn 2 remains in Herceptin/HER2 context without requiring the drug name again  
**And** answers remain research-assist bounded (FR12 / AD-14)  
**And** Source Identifiers (PMID and/or NCT and/or ChEMBL) appear when corresponding tools return them (FR11)

## Epic 4: Secure streaming research turns

SSE Stream Events via Stream Lambda; Runtime never invoked from the browser; tool failures stream `error` and session continues.

**FRs covered:** FR4, FR5, FR8, FR9  
**ADs:** AD-1, AD-4, AD-5, AD-7 (`sessionId`), AD-8, AD-12  
**NFRs:** NFR1, NFR8, NFR9, NFR10

### Story 4.1: Stream Lambda SSE bridge to AgentCore Runtime

As a builder,
I want a Stream Lambda that invokes Runtime and emits SSE Stream Events,
So that clients never call AgentCore directly (FR8, AD-1, AD-4).

**Acceptance Criteria:**

**Given** AgentCore Runtime from Epic 3 is available  
**When** an authenticated test client opens the Stream Lambda Function URL and starts a turn  
**Then** the response is SSE with event types from `session_started` | `reasoning` | `token` | `tool_use` | `tool_result` | `error` | `done`  
**And** `session_started` includes a Stream-owned `sessionId` passed through to Runtime/Memory on subsequent events in the turn  
**And** `done` is emitted only after the Runtime turn stream closes (or hard abort)  
**And** documentation and client samples do not instruct browser→AgentCore Runtime invoke or embed Runtime IAM credentials

### Story 4.2: Cognito Identity Pool + SigV4 to Function URL

As a builder,
I want UI→Stream auth via User Pool → Identity Pool → SigV4 IAM on the Function URL,
So that AD-1 is enforceable before the React UI lands (FR8, NFR1).

**Acceptance Criteria:**

**Given** Cognito User Pool and Identity Pool are wired so authenticated users can obtain temporary credentials authorized for the Stream Function URL  
**When** a request is SigV4-signed with those Identity Pool credentials  
**Then** the stream endpoint accepts the request  
**When** the request is unauthenticated or unsigned  
**Then** the stream endpoint rejects it  
**And** a JWT-authorizer-on-Function-URL path is not implemented as a V1 alternate

### Story 4.3: Map tool activity + failures to Stream Events

As a scientist,
I want visible `tool_use` / `tool_result` and a streamed `error` on tool failure without killing the session,
So that FR5 and FR9 hold over the stream path (AD-5, AD-8).

**Acceptance Criteria:**

**Given** Stream Lambda from Stories 4.1–4.2 and Gateway tools from Epic 2  
**When** a turn invokes at least one V1 tool (e.g. PubMed)  
**Then** at least one `tool_use` event is emitted before `done`  
**And** corresponding `tool_result` events include `tool`, `status`, and `ids` when status is `ok`  
**When** a tool failure is forced/simulated  
**Then** a `tool_result` with `status: error` is emitted, then an `error` Stream Event, and a later turn on the same `sessionId` still works  
**And** `reasoning` events are emitted only if Runtime/Strands exposes thinking content — never fabricated from answer tokens

### Story 4.4: Stream observability + stall terminal state

As a builder,
I want structured logs and a soft 5-minute stall terminal,
So that failed demos are debuggable without leaving infinite spinners (NFR9, NFR10, AD-12).

**Acceptance Criteria:**

**Given** Stream Lambda is handling a turn  
**When** the turn runs (success or failure)  
**Then** CloudWatch logs include structured fields `sessionId`, `requestId`, and `tool` when applicable  
**And** the Stream Lambda log group retention is **7 days**  
**And** if the stream stalls with no terminal event, the client or test harness shows a terminal error/timeout state within **5 minutes**

## Epic 5: Authenticated research chat

Asha signs in (Cognito), chats with Disclaimer + live tool_use/answer stream (SigV4), follow-up works, signs out.

**FRs covered:** FR1–FR7, FR5, FR17 (E2E)  
**ADs:** AD-1, AD-10, AD-14  
**NFRs:** NFR2, NFR4

### Story 5.1: Vite React app scaffold + Cognito sign-in/out

As a scientist,
I want to sign in with Cognito email/password and sign out,
So that only authenticated users reach chat (FR1, FR2, FR7, AD-10).

**Acceptance Criteria:**

**Given** Cognito User Pool and app client configuration available to `web/`  
**When** I open the app and sign in with valid email/password  
**Then** I can reach the chat surface  
**When** credentials are invalid  
**Then** a clear auth error is shown and no Chat Session starts  
**When** I sign out  
**Then** subsequent chat/stream actions require sign-in again  
**And** the UI does not offer public self-registration  
**And** docs or README reference manual admin/CLI create-user using pool/client outputs (FR2)

### Story 5.2: Chat UI with Disclaimer + SigV4 stream client

As a scientist,
I want a chat page that shows the research Disclaimer and streams turns via SigV4 to the Stream URL,
So that FR3–FR6 and AD-1 hold in the UI.

**Acceptance Criteria:**

**Given** an authenticated user from Story 5.1 and Stream URL + Identity Pool from Epic 4  
**When** I open the chat surface  
**Then** the approved Disclaimer is visible without requiring a separate legal-only page as the sole placement  
**When** I submit a non-empty message  
**Then** a stream turn starts using Cognito Identity Pool credentials + SigV4 to the Function URL (not Runtime IAM in the browser)  
**When** I submit an empty message  
**Then** the agent/stream is not invoked  
**And** the UI renders `token` text progressively, renders `reasoning` if present, and ignores unknown Stream Event types without crashing

### Story 5.3: Render tool_use / tool_result / error in the transcript

As a scientist,
I want live tool activity and errors in the UI,
So that tool-use visibility and failure continuity are obvious (FR5, FR9).

**Acceptance Criteria:**

**Given** the chat UI from Story 5.2  
**When** a turn invokes a V1 Gateway Tool  
**Then** the UI shows the tool name from at least one `tool_use` event before or while the answer streams  
**When** an `error` Stream Event is received (e.g. forced tool failure)  
**Then** the UI shows a safe error message and does not crash  
**And** I can submit another message in the same Chat Session after the failed turn

### Story 5.4: Herceptin E2E multi-turn in the UI

As a scientist,
I want mechanism → cardiotoxicity follow-up in the hosted chat,
So that UJ-1 and FR17 work end-to-end with source traceability.

**Acceptance Criteria:**

**Given** Stories 5.1–5.3 and backend from Epics 2–4  
**When** after login I ask “What is the mechanism of action of Herceptin?”  
**Then** I see `tool_use` activity and a streamed answer, with PMID/NCT/ChEMBL IDs surfaced when tools returned them  
**When** I ask a follow-up “Which patient populations are most vulnerable to its cardiotoxicity?” without restating the drug name  
**Then** the answer remains in Herceptin/HER2 context  
**And** if the stream stalls with no terminal event, the UI shows a terminal error/timeout within **5 minutes**

## Epic 6: Deployable pilot lifecycle

Dev CDK-deploys the slice, uses documented Outputs, runs smoke demo, destroys cleanly.

**FRs covered:** FR18–FR21  
**ADs:** AD-11, AD-12, AD-13  
**NFRs:** NFR3, NFR12, NFR13

### Story 6.1: CDK Backend stack (auth, stream, runtime, gateway, tools, memory)

As a builder,
I want a TypeScript CDK Backend that wires Cognito + Identity Pool, Stream Function URL, Runtime, Gateway + 3 tools, Memory, and least-privilege IAM with 7-day logs,
So that the cloud path is deployable as one unit (FR18, AD-11, AD-12).

**Acceptance Criteria:**

**Given** application code from Epics 1–5 exists as deployable assets  
**When** I run the documented Backend `cdk deploy` in `us-east-1` (or CDK context region) with Bedrock model access enabled  
**Then** the Backend stack deploys successfully  
**And** Outputs include at least `UserPoolId`, `UserPoolClientId`, `IdentityPoolId`, `StreamUrl` (plus Runtime/Gateway identifiers needed to operate)  
**And** IAM roles follow AD-12 (Stream invokes Runtime + logs; Runtime invokes Bedrock pin + Gateway + Memory + logs; each tool Lambda only its API + logs)  
**And** CloudWatch log groups created by the app use **7-day** retention  
**And** no secrets, API keys, or AWS credentials are committed to the repo (NFR3)

### Story 6.2: CDK Frontend stack (S3 + CloudFront + web config)

As a builder,
I want Frontend hosting for `web/` with CloudFront HTTPS and injected config,
So that Asha can open the demo URL (FR18, NFR4, AD-11).

**Acceptance Criteria:**

**Given** Backend Outputs from Story 6.1 and a production Vite build of `web/`  
**When** I deploy the Frontend stack  
**Then** S3 + CloudFront host the app and Output `FrontendUrl` is published  
**And** the deployed app is configured with Cognito User Pool/Client, Identity Pool, and Stream URL from Backend Outputs  
**And** the site is served over HTTPS via CloudFront

### Story 6.3: Documented Outputs + create-user + smoke path

As a builder,
I want docs for Outputs, admin user create, and Herceptin smoke,
So that a demo works in under 15 minutes after deploy (FR19, FR21, SM-1).

**Acceptance Criteria:**

**Given** Backend and Frontend are deployed  
**When** I follow `docs/` (and/or README) install/deploy/create-user/smoke instructions alone  
**Then** required CDK Outputs are listed with how to use them  
**And** Cognito admin/CLI create-user steps succeed using those Outputs  
**And** the smoke path covers login → Herceptin mechanism question → visible `tool_use` + streamed answer  
**And** docs use honest scope language (research assist; not clinical-grade / proprietary KG / validated-target platform)

### Story 6.4: CDK destroy + teardown docs

As a builder,
I want `cdk destroy` to remove app stacks and docs that call out leftovers,
So that idle cost stays controlled (FR20, NFR12).

**Acceptance Criteria:**

**Given** app stacks from Stories 6.1–6.2 are deployed  
**When** I run the documented destroy command(s)  
**Then** Backend and Frontend application stacks are removed  
**And** docs note any retained resources (e.g. CDK bootstrap, log groups retention leftovers)  
**And** README/docs emphasize destroy-when-not-demoing as the default operating model
