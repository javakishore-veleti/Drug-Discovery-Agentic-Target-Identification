---
stepsCompleted: [step-01-validate-prerequisites, step-02-design-epics]
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
