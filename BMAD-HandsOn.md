# BMAD Hands-On

## Step - 01 My prompt to Cursor - Use the bmad-help skill:

```text
Use the bmad-help skill. This is a greenfield drug-discovery / target-identification agent platform on AWS Bedrock AgentCore. What is the first BMAD workflow I should run, and run it with me step by step.
```

## Step - 01 Cursor Response:

```text
Where you are

BMad Method · Phase 1 (analysis) — greenfield. _bmad-output/planning-artifacts and docs are empty. The README already sketches vision, AgentCore architecture, and biomedical tools, but there is no brief, PRD, or architecture artifact yet.

What to run first
Optional (Phase 1) — worth considering
[DR] Domain Research — bmad-domain-research — drug-discovery / target-ID terminology and landscape
[TR] Technical Research — bmad-technical-research — AgentCore / MCP feasibility deep dive
[BP] Brainstorm Project — bmad-brainstorming — if you want to expand beyond the README
Recommended first workflow (start here)
[CB] Create Brief — bmad-product-brief

You already have a clear concept, so a product brief is the right first formal artifact. It locks problem, users, scope, and success before the required PRD.

Next required (after the brief)
[PRD] Create Edit and Review PRD — bmad-prd (required gate into planning)

Tip: run later skills in a fresh chat when you move on; we can finish the brief in this one.

Starting Create Brief with you now
javakishore-veleti — kicking off Create Brief for this AgentCore target-identification platform.

You can call bmad-party-mode for multi-agent debate or bmad-advanced-elicitation for deeper critique anytime.

I’ve read the README as source material. Intent looks like create (no prior brief). Confirm if that’s right, or say if you meant update/validate something else.

Discovery — Step 1: brain dump
Before we draft anything, put the full picture on the table. Dump freely — messy is fine:

What this product must become (beyond the README)
Who it’s for (pharma scientists? AWS sample demo? both?)
Why you’re building it (sample, internal platform, product, learning?)
What “done for v1” means
Any constraints (AWS-only, compliance, no real patient data, timeline, etc.)
Also: any other source material? (memo, deck, prior brief, Slack thread, competitor notes)

After that I’ll ask one “anything else?”, then we’ll pick Fast path (batched Qs + draft with [ASSUMPTION] tags) or Coaching path (section-by-section).

```

## Step 02 - My next reply to Curose

```text

Create — yes. No prior brief. README is the only source material so far (plus an AWS AgentCore target-ID sample I’ve studied for architecture patterns).

## What this product must become
An agentic drug-discovery platform focused on target identification. Pharma researchers chat with a unified research agent on AWS Bedrock AgentCore. The agent uses an MCP-style gateway to call biomedical tools (PubMed, ChEMBL, ClinicalTrials, etc.) and synthesizes evidence on mechanism, safety, pathways, patient risk, and design hypotheses.

V1 is a working vertical slice, not 30+ tools:
- Cognito login
- React chat UI with streaming
- Stream Lambda → AgentCore Runtime
- Unified Research Agent (Python / Strands / Claude on Bedrock)
- Gateway with 3–5 tools (start: PubMed, ClinicalTrials, ChEMBL)
- Session memory
- CDK deploy/destroy

Not in v1: Federate/Midway, USPTO (optional later), FAERS/Athena, multi-agent swarm in production, heavy WAF/pipeline polish.

## Who it’s for
Primary: drug discovery scientists / computational biologists exploring targets (demo persona: Herceptin / HER2 safety & design questions).
Secondary: me as builder — ship a real AgentCore platform I understand end-to-end.
Not for: real clinical decision-making or PHI/patient records.

## Why I’m building it
Own productized platform on AWS AgentCore for target-identification research workflows. Public positioning is a drug-discovery agent product (README already states that). I’m using BMAD for planning instead of Kiro.

## What “done for v1” means
1. Deploy to my AWS account with CDK
2. Log in, ask a Herceptin-style question, see tool_use + answer stream
3. Multi-turn session remembers context
4. I can destroy stacks cleanly
5. I can add one new tool in under a day

## Constraints
- AWS us-east-1 (or my default region), Bedrock model access required
- No real patient data; public biomedical APIs only
- Cognito email/password (no Midway/Federate)
- Cost-conscious: tear down when not demoing
- Prefer Cursor + BMAD for process; keep planning light (brief → PRD → architecture → phased build)
- Reference architecture exists conceptually (AgentCore + gateway + stream UI); do not copy proprietary sample code into this repo

## Success metrics (v1)
- End-to-end demo works in <15 minutes after deploy
- At least 3 tools callable via gateway
- Clear docs for install/deploy/destroy

Prefer Fast path after this dump unless you see a critical gap.

```

## Step - 02 - Cursor Response To The Above

```text
Dump is strong enough for Fast path — no critical gaps. One consolidated check, then I draft with [ASSUMPTION] tags where I fill in.

Anything else?
Anything you almost forgot (must-have demo narrative, branding, hard deadlines, must-use AWS services)?

Fast-path gaps (answer in one short reply)
A. Product name for the brief title / UI

Keep repo-style: Drug Discovery Agentic Target Identification, or
Shorter working name (e.g. TargetID Agent, Agentic Target ID)?
B. Differentiation (confirm or rewrite)
Suggested framing from landscape scan:
AWS-native governed research copilot that unifies public biomedical evidence through AgentCore + MCP — forkable discovery desk research, not a BenchSci/Insilico-grade validated target platform.
Win on: time-to-pilot, streaming tool-use transparency, CDK deploy/destroy, easy tool add.
Do not claim: proprietary knowledge graph, closed-access lit, clinical-grade ranking.

Reply with A + B (and anything else, or “nothing else / draft it”). I’ll write the full brief next.
```

### Step - 03 - My Response to Cursor

```text
A. Working name: Agentic Target ID
   Full / repo name: Drug Discovery Agentic Target Identification (keep for GitHub/README)

B. Differentiation — confirmed as you framed it:
AWS-native governed research copilot that unifies public biomedical evidence through AgentCore + MCP — forkable discovery desk research, not a BenchSci/Insilico-grade validated target platform.
Win on: time-to-pilot, streaming tool-use transparency, CDK deploy/destroy, easy tool add.
Do not claim: proprietary knowledge graph, closed-access lit, clinical-grade ranking.

Anything else:
- Demo narrative: Herceptin / HER2 — mechanism, cardiotoxicity risk, pathway context, safer targeting hypotheses
- Branding: keep technical/professional; no fake “enterprise validated” claims
- Hard deadline: none — cost-conscious demos, tear down when idle
- Must-use AWS: Bedrock + AgentCore Runtime, AgentCore Gateway (MCP), Cognito, Lambda stream, CDK; S3/CloudFront for UI

Nothing else — draft it.
```

## Step 03 - Cursor Response For The Above

```text
Draft is ready for review:
_bmad-output/planning-artifacts/briefs/brief-Drug-Discovery-Agentic-Target-Identification-2026-07-25/brief.md

What’s in it
Working name Agentic Target ID, your V1 slice, Herceptin/HER2 demo, confirmed differentiation, in/out scope, must-use AWS, success criteria, and constraints.

Two [ASSUMPTION] tags to confirm or rewrite
Success: demo answers surface source IDs (PMID / NCT / ChEMBL) enough to spot-check.
Post-V1: Open Targets–style structured evidence + pathway tools before multi-agent orchestration.
Reply with edits (or “looks good / finalize”) and I’ll lock the brief (polish pass + status update). Next BMAD step after that is [PRD] bmad-prd in a fresh chat.

```

## Step 04 - My Reply to Cursor

```text
Looks good — finalize.

ASSUMPTION 1 (source IDs): Confirmed. V1 demo answers should surface PMID / NCT / ChEMBL IDs enough to spot-check.

ASSUMPTION 2 (post-V1): Confirmed. After V1, prioritize Open Targets–style structured evidence + pathway tools before multi-agent orchestration.

No other edits. Lock the brief, then I’ll start [PRD] bmad-prd in a fresh chat.
```

## Step 04 - Cursor Reponse To The Above

```text

Locking the brief: confirming assumptions, running finalize polish, and updating status.

Confirming assumptions and running structure + prose polish in parallel.

Applying confirmed assumptions and high-value polish, then locking status to final.

Brief locked. status: final

Path: _bmad-output/planning-artifacts/briefs/brief-Drug-Discovery-Agentic-Target-Identification-2026-07-25/brief.md

Memlog audit
Memlog item	Disposition
Create / Fast path / README + patterns-only
In brief (constraints + scope out)
V1 slice + tool set + CDK lifecycle
In brief (summary, solution, scope, success)
Out of V1 / no PHI / not clinical
In brief (who, scope out, differentiation table)
Users + productized AgentCore positioning
In brief
Working vs repo name
In brief header
Differentiation framing
In brief (table + comps line)
Herceptin demo + must-use AWS
In brief (solution, scope in)
Source IDs + post-V1 Open Targets/pathways
Confirmed → Success Criteria + Vision
BMAD process line
Process noise → memlog only (not in brief)
Addendum
Not needed
What’s next (fresh chat)
[PRD] Create Edit and Review PRD — bmad-prd
Point it at this brief. Optional before PRD: Domain/Technical research — skip if you want to stay light. After PRD: Architecture → Epics → Implementation Readiness.

Suggested opener for the new chat:
Use bmad-prd to create a PRD from the finalized product brief at
_bmad-output/planning-artifacts/briefs/brief-Drug-Discovery-Agentic-Target-Identification-2026-07-25/brief.md

```

## Step - 05 - My Reply To Cursor

```text
Create — yes. Brief is the primary intake. Also use README.md as secondary product language (public positioning). No other drafts.

## What the PRD must cover that the brief underplays
1. End-to-end user journeys (login → new session → ask → stream tool_use/answer → follow-up → logout)
2. Functional requirements for: Cognito auth, Stream Lambda contract, AgentCore Runtime agent, Gateway tools (PubMed / ClinicalTrials / ChEMBL), session memory, frontend event types
3. Non-functional: security (no browser→AgentCore direct invoke), cost teardown, observability (basic logs), latency expectations for demo (best-effort, not SLA)
4. Explicit acceptance criteria per capability (testable)
5. Data boundaries: public APIs only; no PHI; research-assist disclaimer in UI
6. Tool response contract: surface PMID / NCT / ChEMBL IDs in answers when available
7. Failure modes: tool timeout/error should stream an error event and still allow conversation to continue
8. Deploy/destroy as first-class requirements (CDK outputs documented)

## Hard non-negotiables (V1)
- AWS: Bedrock + AgentCore Runtime + AgentCore Gateway (MCP) + Cognito + Lambda stream + CDK; S3/CloudFront for UI
- Auth: Cognito email/password only (no Midway/Federate)
- No real patient/PHI data
- Do not copy proprietary sample code from external repos — patterns/architecture only
- Do not claim clinical-grade / proprietary KG / validated-target platform
- V1 tools start with PubMed, ClinicalTrials.gov, ChEMBL (3 minimum; up to 5 if easy)

## Do not write into V1 PRD as requirements
- USPTO, FAERS/Athena, multi-agent orchestration, Federate SSO, heavy WAF/CI, closed literature corpora

## Success / demo bar (unchanged, make measurable)
- Deploy with CDK → demo in <15 minutes
- Herceptin/HER2 narrative works with visible tool_use + streamed answer
- Multi-turn memory works for one follow-up
- Destroy cleans app stacks
- Source IDs (PMID/NCT/ChEMBL) appear when tools return them

## Stakes
Internal / builder + demoware product slice — not a public paid launch. Optimize for clarity and shippability over enterprise completeness.

Prefer Fast path after this dump.
```

## Step - 05 - Cursor Response

```text
Fast-path gaps (answer in one reply; defaults noted)
1. Streaming event types (frontend contract)
README only says SSE + tool-use visibility. Propose V1 minimum: session_started | token | tool_use | tool_result | error | done
OK as-is, or rename/add?

2. Auth / user provisioning
Default: Cognito email/password; manual admin create user post-deploy (no self-signup UI in V1). OK?

3. Session memory
Default: within one browser session / AgentCore session — one follow-up must remember prior turns; no cross-day resume list UI in V1. OK?

4. Demo latency (best-effort, not SLA)
Default target: first tool_use visible <30s on a warm path; full answer often 1–3 min depending on tools. Soft expectation in NFR only. OK?

5. Fourth/fifth tools
Default: ship exactly 3 (PubMed, ClinicalTrials.gov, ChEMBL). Tools 4–5 deferred unless trivial. Confirm?

6. Research disclaimer copy
Default UI line: “Research assistance only. Not medical advice. Verify claims against primary sources (PMID / NCT / ChEMBL IDs). Not for clinical decision-making.” OK or rewrite?

7. Named journey personas
Default: Asha (computational biologist, Herceptin/HER2 desk research) + Dev (builder: deploy → demo → destroy → add tool). OK?

Reply with yes/overrides. I’ll then draft the full PRD with [ASSUMPTION] tags only where still inferred.
```

## Step - 06 - My Reply To Cursor

```text
1. Streaming events — OK with one tweak for clarity:
   session_started | reasoning | token | tool_use | tool_result | error | done
   (add optional `reasoning` for “thinking”/plan text; `token` for answer stream. If you prefer fewer types, drop `reasoning` and fold into `token`.)

2. Auth — Yes. Cognito email/password; manual admin create user post-deploy; no self-signup UI in V1.

3. Session memory — Yes. Multi-turn within one AgentCore/browser session; one follow-up must remember prior turns; no cross-day resume/list UI in V1.

4. Demo latency — Yes. Soft NFR only: first tool_use <30s warm path; full answer often 1–3 min. Not an SLA.

5. Tools — Yes. Ship exactly 3: PubMed, ClinicalTrials.gov, ChEMBL. 4–5 deferred.

6. Disclaimer — OK as written.

7. Personas — Yes. Asha (computational biologist, Herceptin/HER2) + Dev (builder: deploy → demo → destroy → add tool).

No other overrides — draft the full PRD.
```

## Step - 06 - Cursor Response
```text
Drafting the full PRD from your confirmed answers, then logging the decisions.

Draft ready (status: draft).

Paths

PRD: _bmad-output/planning-artifacts/prds/prd-Drug-Discovery-Agentic-Target-Identification-2026-07-25/prd.md
Addendum: .../addendum.md (mechanism, API limits, deferred tools, approved disclaimer)
What’s in the PRD

UJ-1 Asha (login → session → stream → follow-up → logout) · UJ-2 Dev (deploy → demo → destroy → extend)
FR-1–FR-21 with testable consequences: Cognito, Stream Events (session_started | reasoning | token | tool_use | tool_result | error | done), Stream Lambda security path, agent, 3 tools, source IDs, session memory, CDK deploy/destroy/outputs/docs
NFRs: security, soft latency, failure streaming, basic logs, cost teardown
SM-1–SM-7 + counter-metrics · 7 [ASSUMPTION] tags indexed
Review the draft and tell me what to change. When you’re happy, say finalize and I’ll run memlog audit → input reconciliation → reviewer gate → polish → mark status: final.

```

## Step - 07 - My Reply To Cursor

```text
Looks good — finalize.

No content edits. Assumptions 1–7 accepted as written.
Open questions 1, 3, 4, 5 → architecture.
Open question 2 → document soft UI stall timeout as 5 minutes in polish if you want a default; otherwise leave to architecture.

Proceed: memlog audit → input reconciliation → reviewer gate → polish → status: final.
```

## Step - 08 Cursor Reply For The Above
```text
Proceeding through finalize: auditing the memlog, reconciling inputs, then reviewer gate and polish.

Memlog audit complete — all decisions land in PRD, addendum, or deferred-to-architecture. Running input reconciliation and the rubric reviewer in parallel.

PRD finalized (status: final).

Artifact: _bmad-output/planning-artifacts/prds/prd-Drug-Discovery-Agentic-Target-Identification-2026-07-25/prd.md
Addendum: .../addendum.md (incl. §J finalize dispositions)

Step	Result
Memlog audit
All decisions in PRD, addendum, or deferred
Input reconciliation
Brief/README deltas intentional or non-blocking — see addendum §J
Reviewer gate
Strong — 0 critical / 0 high; medium/low → architecture/stories
Polish
NFR-9 stall timeout 5 min; OQs dispositioned; assumptions accepted
Close
status: final
Common next: bmad-ux, bmad-architecture, or bmad-create-epics-and-stories — or bmad-help for routing.

```

## Step - 09 - My Reply To Cursor
```text
Use bmad-create-architecture (or bmad-architecture).
PRD is final at:
_bmad-output/planning-artifacts/prds/prd-Drug-Discovery-Agentic-Target-Identification-2026-07-25/prd.md
Addendum: .../addendum.md

Design the V1 architecture for Agentic Target ID against that PRD (AgentCore Runtime, Gateway + 3 tools, Stream Lambda, Cognito, React/CloudFront, CDK). Prefer Fast path. Resolve PRD open questions where architecture owns them (model ID pin, whether reasoning events are available, IAM/log retention defaults).

Skip bmad-ux for now — chat UI is thin; architecture unblocks build sooner. After architecture: bmad-create-epics-and-stories, then Phase 1 code.

Optional now: commit _bmad/, .agents/, .gitignore, and _bmad-output/planning-artifacts/ so brief + PRD are on GitHub.

```

## Step - 09 - Cursor Response
```text
Starting architecture from the finalized PRD — reading the BMAD architecture skill and kicking off Fast path.

Activating bmad-architecture (create). Resolving workflow config and checking for an existing spine run.

javakishore-veleti — starting Create Architecture via bmad-architecture (create intent).
Note: bmad-create-architecture is deprecated; this run uses bmad-architecture.

Workspace: _bmad-output/planning-artifacts/architecture/architecture-Drug-Discovery-Agentic-Target-Identification-2026-07-25/
Input: final PRD + addendum · Mode: Fast path (from your HandsOn note) · UX: skipped for now

One question before I draft the spine:

Is the architecture spine the only deliverable?
I’m assuming yes — a lean build substrate for you (solo builder) so epics/stories and Phase 1 CDK/AgentCore code don’t drift. No discussion deck / long solution-design doc unless you want one.

Reply with:

Spine only (default), or
Spine + something else (what / for whom)
Then I’ll draft the full V1 spine with [ASSUMPTION] tags, resolve the PRD open questions architecture owns (model ID, reasoning events, IAM/log retention), and you can correct in review.

```

# Step - 10 - My Reply To The Above
```text
Spine only (default).

Lean build substrate for solo builder — enough that epics/stories and Phase 1 CDK/AgentCore code don’t drift. No discussion deck / long solution-design doc.

Resolve PRD open questions you own (model ID pin, reasoning events availability, IAM/log retention defaults) with [ASSUMPTION] tags where needed. Draft the full V1 spine.
```

## Step - 10 - Cursor Response
```text

Draft spine ready (status: draft).

Path: _bmad-output/planning-artifacts/architecture/architecture-Drug-Discovery-Agentic-Target-Identification-2026-07-25/ARCHITECTURE-SPINE.md

Spine shape
Paradigm: layered request path + single-agent tool loop
AD-1…AD-14 — secure stream, single agent, 3 tools, Stream Events, memory, errors, source IDs, Cognito, CDK outputs, IAM/logs, dependency direction, data boundary
Stack pins (web-checked): CDK ^2.262, Node 22, Python 3.12, strands-agents ^1.47
Structural seed matches README dirs (agents/, gateways/, infra/, web/)
PRD open questions resolved
OQ	Decision
Model ID
Pin us.anthropic.claude-sonnet-4-20250514-v1:0 (AD-6); fallback noted if account blocks
reasoning events
Emit only if runtime exposes thinking; never fabricate; UI optional (AD-5)
Log retention
7 days on app log groups (AD-12)
Assumptions to confirm
Sonnet 4 US profile enabled in your account
V1 OK if zero reasoning events
Vite + React 18+ for web/
Stream Lambda in Python 3.12
Gateway targets = Lambdas
Review and say what to change — or finalize to run reconcile → reviewer gate → status: final.
```

## Step - 11 - My Reply To Cursor
```text
Looks good — finalize.

Assumptions:
1. Keep Sonnet 4 pin (us.anthropic.claude-sonnet-4-20250514-v1:0); fallback path in AD-6 stands if account blocks it.
2–5: Confirmed as written.

Optional polish: note preferred Stream auth = Cognito Identity Pool credentials + SigV4 to Function URL (or JWT authorizer) — browser never holds Runtime IAM. Otherwise no content edits.

Proceed: reconcile → reviewer gate → status: final.
```

## Step - 11 - Cursor Response
```text
Finalizing the spine: applying the Stream auth polish, then reconcile and reviewer gate.

Gate verdict: adequate — applying clear fixes for the auth fork and adversarial holes, then marking final.

Architecture spine finalized (status: final).

Path: _bmad-output/planning-artifacts/architecture/architecture-Drug-Discovery-Agentic-Target-Identification-2026-07-25/ARCHITECTURE-SPINE.md

Gate step	Result
Lint
0 findings
Reconcile PRD
1 gap → closed with AD-15 (tool 429/backoff/45s timeout)
Rubric
adequate → highs fixed
Versions
PASS
Adversarial
forks closed (auth, sessionId, ids, done ordering, env names)
Gate fixes applied: AD-1 locks Cognito Identity Pool + SigV4 (JWT authorizer deferred); AD-7 Stream owns sessionId; AD-9 flat ids on tool_result; AD-4/done ordering; AD-14 FR-12 prompt rule; AD-15 tool resilience.

Next (per HandsOn): bmad-create-epics-and-stories, then Phase 1 code. Optional: commit _bmad/, .agents/, .gitignore, and _bmad-output/planning-artifacts/ when you want them on GitHub.
```

## Step - 12 - My Reply To Cursor
```text
Use bmad-create-epics-and-stories.
Inputs (all final):
- Brief: _bmad-output/planning-artifacts/briefs/brief-Drug-Discovery-Agentic-Target-Identification-2026-07-25/brief.md
- PRD: _bmad-output/planning-artifacts/prds/prd-Drug-Discovery-Agentic-Target-Identification-2026-07-25/prd.md
- Architecture spine: _bmad-output/planning-artifacts/architecture/architecture-Drug-Discovery-Agentic-Target-Identification-2026-07-25/ARCHITECTURE-SPINE.md

Create V1 epics/stories that map to FR-1..FR-21 and AD-1..AD-15.
Prefer a phased order matching hands-on build: (1) local agent + PubMed tool, (2) gateway + 3 tools, (3) AgentCore Runtime, (4) Stream Lambda + SigV4, (5) Cognito + React UI, (6) CDK deploy/destroy + docs.
Keep stories small enough for one focused coding session each.
```

## Step - 12 - Cursor Response
```text
Creating V1 epics and stories from the final brief, PRD, and architecture spine — reading the skill and following its workflow.

javakishore-veleti — starting Create Epics and Stories.

Prerequisites found
Input	Path	Status
Brief
_bmad-output/planning-artifacts/briefs/brief-Drug-Discovery-Agentic-Target-Identification-2026-07-25/brief.md
final
PRD
_bmad-output/planning-artifacts/prds/prd-Drug-Discovery-Agentic-Target-Identification-2026-07-25/prd.md
final
Architecture spine
_bmad-output/planning-artifacts/architecture/architecture-Drug-Discovery-Agentic-Target-Identification-2026-07-25/ARCHITECTURE-SPINE.md
final
UX design contract
—
Not found (matches prior “skip UX” call)
Also available if you want it: PRD addendum.md, architecture reviews/, README.md.

Before I extract FRs/NFRs into epics.md:

Include any other documents (e.g. PRD addendum, README)?
Exclude any of the three finals above?
Reply with include/exclude choices (or “use the three as listed + PRD addendum”), then I’ll extract requirements and pause for [C] continue.
```

## Step - 13 - My Reply To Cursor
```text
Use the three finals as listed + PRD addendum.md.

Also include README.md as secondary (demo prompts + public positioning language only — do not expand V1 scope from the README tool catalog).

Exclude: UX design contract (none), architecture reviews/ (unless needed for a conflict).

Then extract FRs/NFRs and pause for [C] continue.

Also worth doing soon: commit BMAD scaffolding + planning artifacts so brief/PRD/architecture are on GitHub before you start coding stories.

```

## Step - 13 - Cursor Response
```text
Extracting FRs/NFRs from the confirmed inputs and initializing epics.md.

Requirements extracted into _bmad-output/planning-artifacts/epics.md (step-01).

Inputs used: brief + PRD + addendum + architecture spine + README (secondary). UX excluded.

Functional Requirements — 21
Examples: FR1 Cognito sign-in · FR4 Stream Events · FR8 secure stream path · FR13–16 three tools · FR18–21 CDK/docs
Full list is in epics.md.

Non-Functional Requirements — 13
Security path (NFR1–4), soft latency (NFR5–7), failure/stall (NFR8–9), logs/cost (NFR10–13).

Additional (Architecture)
AD-1…AD-15, stack pins, structural seed dirs, env names, hands-on build phasing (1→6) as epic-ordering constraint. README tool catalog explicitly not in scope.

UX Design Requirements
None (skipped).

Do these accurately represent what needs to be built? Any additions or corrections?

Confirm the Requirements are complete and correct to [C] continue:

(Optional soon, separate from this workflow: commit BMAD scaffolding + planning artifacts before coding stories — say the word when you want that.)

```

## Step 14 - My Reply To Cursor
```text
[C] continue

Requirements look complete and correct. No additions.
Keep the hands-on phasing (1→6) as the epic order constraint.
```

## Step 14 - Cursor Reply
```text
Continuing to epic design — loading and following step 02.

Proposed 6 epics aligned to hands-on phasing (1→6), framed as user outcomes (not bare tech layers). Stories come next — not in this step.

Epic List (proposed)
Epic 1: Local literature research loop
Builder/scientist can run a Herceptin-style question locally against a Strands agent + PubMed and see PMIDs in the answer.
FRs: FR10 (partial), FR11 (PMID), FR12, FR13
ADs: AD-2, AD-5 (prompt), AD-6, AD-9 (pubmed ids), AD-14

Epic 2: Governed three-tool evidence gateway
Agent can call PubMed, ClinicalTrials.gov, and ChEMBL through AgentCore Gateway with normalized ids, timeouts/429 handling, and error-shaped results.
FRs: FR13–FR16, FR9 (tool path), FR11
ADs: AD-3, AD-8, AD-9, AD-15

Epic 3: AgentCore Runtime + session memory
Unified Research Agent runs on AgentCore Runtime with pinned model and in-session multi-turn memory (follow-up remembers Herceptin context).
FRs: FR10, FR12, FR17
ADs: AD-2, AD-6, AD-7 (Memory), AD-14

Epic 4: Secure streaming research turns
Client (then UI) receives SSE Stream Events via Stream Lambda; Runtime is never invoked from the browser; tool failures stream error and session continues.
FRs: FR4, FR5, FR8, FR9
ADs: AD-1, AD-4, AD-5, AD-7 (sessionId), AD-8, AD-12 (stream logs)
NFRs: NFR1, NFR8, NFR9, NFR10

Epic 5: Authenticated research chat
Asha signs in (Cognito), chats with Disclaimer + live tool_use/answer stream (SigV4), follow-up works, signs out.
FRs: FR1–FR7, FR5, FR6, FR17 (E2E)
ADs: AD-1, AD-10, AD-14
NFRs: NFR2, NFR4

Epic 6: Deployable pilot lifecycle
Dev CDK-deploys the slice, uses documented Outputs, runs smoke demo, destroys cleanly.
FRs: FR18–FR21
ADs: AD-11, AD-12, AD-13
NFRs: NFR3, NFR12, NFR13
SMs: SM-1, SM-5, SM-6

FR Coverage Map (proposed)
FR	Epic
FR1–FR3, FR6–FR7
Epic 5
FR4–FR5, FR8–FR9
Epic 4 (FR9 also Epic 2 tool surface)
FR10, FR12
Epic 1 → completed in Epic 3
FR11
Epic 1 (PMID) → Epic 2 (all ids)
FR13
Epic 1 local → Epic 2 Gateway
FR14–FR16
Epic 2
FR17
Epic 3 → verified E2E in Epic 5
FR18–FR21
Epic 6
Soft latency NFR5–NFR7: validated in Epic 5/6 demo, not separate epics.

Does this epic structure align with your vision? Any regrouping?

Do you approve this epic structure for proceeding to story creation?

Select an Option: [A] Advanced Elicitation [P] Party Mode [C] Continue
```

## Step 15 - My Response To Curosr
```text
[C] Continue

Epic structure approved as proposed (1→6). No regrouping.
Proceed to story creation — keep stories sized for one focused coding session each.
```
## Step 16 - Curosr Response
```text
Saving the approved epic list, then loading story-creation step 03.

Story creation approach: one epic at a time; stories sized for a single focused coding session; Given/When/Then ACs; no forward dependencies within an epic.

Epic 1: Local literature research loop
Goal: Run a Herceptin-style question locally with Strands + PubMed and see PMIDs.
FRs: FR10 (partial), FR11 (PMID), FR12, FR13 · ADs: AD-2, AD-6, AD-9, AD-14

Proposed stories
Story 1.1: Scaffold agent package + pinned Bedrock model
As a builder, I want a runnable agents/unified-research-agent/ package with pinned BEDROCK_MODEL_ID, so that local agent work starts from the architecture stack.
ACs: Given Python 3.12 + Bedrock access · When I install/run the agent entrypoint with a trivial prompt · Then it invokes us.anthropic.claude-sonnet-4-20250514-v1:0 (or documented fallback) · And model id comes from env/config (AD-6) · And no Gateway/UI yet.

Story 1.2: Research-assist system prompt
As a scientist, I want the agent constrained to research assistance, so that answers are not framed as clinical advice (FR12, AD-14).
ACs: Given agent from 1.1 · When I ask a clinical-sounding dosing question · Then the reply refuses actionable clinical orders / states research-only · And prompt includes Disclaimer-equivalent constraints.

Story 1.3: Local PubMed tool with ids.pmid
As a scientist, I want the agent to call a local PubMed tool that returns PMIDs in ids, so that literature answers are spot-checkable (FR13, FR11, AD-9, AD-15 basics).
ACs: Given PubMed reachable · When agent runs Herceptin mechanism query · Then PubMed is invoked · And ok result has ids.pmid (array; empty OK if none) · And 429/timeout ≤45s yields error-shaped result (not hang).

Story 1.4: Local Herceptin synthesis with PMID surfacing
As a scientist, I want a streamed/printed answer that cites PMIDs when present, so that I can spot-check claims (FR10, FR11).
ACs: Given 1.1–1.3 · When I ask “What is the mechanism of action of Herceptin?” · Then agent uses PubMed and returns a synthesis · And at least one PMID appears when tool returned PMIDs · And run completes without Gateway/Runtime/UI.

Does Epic 1’s breakdown look right (scope per story / ACs)?
Reply approve Epic 1 (or edits), and I’ll append it to epics.md and propose Epic 2.
```

## Step 17 - My Reply To Cursor
```text
Approve Epic 1 as proposed (Stories 1.1–1.4).

Optional note only (no change required): 1.1 may create agents/unified-research-agent/ + requirements.txt + README run instructions so 1.2–1.4 have a clear entrypoint.

Append Epic 1 to epics.md and propose Epic 2.
```

## Step 17 - Cursor Reply
```text
Epic 1 appended (Stories 1.1–1.4). Note on scaffold/README captured in 1.1 ACs.

Epic 2: Governed three-tool evidence gateway
Goal: Call PubMed, ClinicalTrials.gov, and ChEMBL via AgentCore Gateway with normalized ids, 429/timeout handling, and error-shaped results.
FRs: FR9 (tool path), FR11, FR13–FR16 · ADs: AD-3, AD-8, AD-9, AD-15

Proposed stories
Story 2.1: Gateway scaffold + PubMed as MCP Lambda target
As a builder, I want PubMed exposed through AgentCore Gateway as MCP tool pubmed, so that the agent calls literature via the governed path (not only local).
ACs: Given Gateway deployable/configurable in account · When agent lists/calls pubmed via Gateway · Then tool runs and returns ids.pmid · And tool name is exactly pubmed (AD-3).

Story 2.2: ClinicalTrials.gov Gateway tool clinicaltrials
As a scientist, I want trial search via Gateway tool clinicaltrials with NCT ids, so that patient-risk/trial context is evidence-backed (FR14).
ACs: When agent calls clinicaltrials · Then ok result has ids.nct array · And 429/≤45s timeout → error-shaped tool_result (AD-15).

Story 2.3: ChEMBL Gateway tool chembl
As a scientist, I want chemistry/bioactivity lookup via Gateway tool chembl, so that design/chemistry claims can cite ChEMBL IDs (FR15).
ACs: When agent calls chembl · Then ok result has ids.chembl array · And same resilience rules as 2.2.

Story 2.4: Enforce exactly three V1 tools + shared error contract
As a builder, I want the default Gateway config to expose only the three tools and a shared failure shape, so that V1 scope stays honest and FR9/AD-8 are consistent (FR16, FR9).
ACs: Given default deploy/config · When tools are listed · Then only pubmed, clinicaltrials, chembl · And forced tool failure returns status: error (+ tool name + short message) suitable for later stream mapping · And agent can continue after a failed tool call in the same local/gateway test session.

Approve Epic 2 (or edits)? I’ll append and propose Epic 3.
```

## Step  - 18 - My Reply To Cursor
```text
Approve Epic 2 as proposed (Stories 2.1–2.4).

Optional note (no structural change): prefer sharing PubMed adapter code between Epic 1 local tool and Gateway Lambda so ids.pmid / timeout behavior stay one implementation.

Append Epic 2 and propose Epic 3.
```

## Step  - 18 - Cursor Response
```text
Epic 2 appended (2.1 includes shared PubMed adapter note).

Epic 3: AgentCore Runtime + session memory
Goal: Unified Research Agent on AgentCore Runtime with pinned model and in-session multi-turn memory.
FRs: FR10, FR12, FR17 · ADs: AD-2, AD-6, AD-7 (Memory), AD-14

Proposed stories
Story 3.1: Containerize agent for AgentCore Runtime
As a builder, I want the Unified Research Agent packaged as a Runtime-deployable container with pinned model config, so that cloud execution matches the local agent (AD-2, AD-6).
ACs: Given Epic 1–2 agent code · When I build the Docker image and deploy/register Runtime · Then Runtime uses BEDROCK_MODEL_ID pin · And single agent entrypoint only (no multi-agent) · And Gateway tools remain reachable from Runtime config.

Story 3.2: Wire AgentCore Memory for Chat Session turns
As a scientist, I want multi-turn context stored in AgentCore Memory for one session, so that follow-ups don’t require restating everything (FR17, AD-7).
ACs: Given Runtime from 3.1 · When two turns run with the same session key · Then Memory retains prior context · And env uses AGENTCORE_MEMORY_ID (no MEMORY_ID alias) · And no session-list/resume UI is built.

Story 3.3: Herceptin multi-turn Runtime smoke (mechanism → cardiotoxicity)
As a scientist, I want a Runtime smoke that answers mechanism then a follow-up on cardiotoxicity without restating Herceptin, so that FR10 + FR17 are proven on AgentCore.
ACs: Given 3.1–3.2 + Gateway tools · When turn 1 asks Herceptin mechanism and turn 2 asks “which patients are most vulnerable to its cardiotoxicity?” · Then turn 2 stays in Herceptin/HER2 context · And answers remain research-assist bounded (FR12) · And Source Identifiers surface when tools return them (FR11).

Approve Epic 3 (or edits)? I’ll append and propose Epic 4.
```

## Step  - 19 - My Reply To Cursor
```text

```