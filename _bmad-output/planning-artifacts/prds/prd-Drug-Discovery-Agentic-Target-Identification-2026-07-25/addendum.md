# Addendum: Agentic Target ID PRD

Companion to `prd.md`. Holds mechanism notes, options considered, and landscape context that should not inflate the requirements narrative. Downstream architecture owns final tech choices.

## A. Reference request path (mechanism)

From README / brief alignment — illustrative, not an FR:

```text
Researcher
  → React UI (CloudFront + S3)
  → Amazon Cognito (auth)
  → Stream Lambda (SSE / SigV4)
  → Bedrock AgentCore Runtime (Unified Research Agent)
       → Foundation model (Claude on Amazon Bedrock)
       → AgentCore Memory (session context)
       → AgentCore Gateway (MCP tools)
            → PubMed | ClinicalTrials.gov | ChEMBL
```

## B. Stream Event type notes

V1 product contract (see PRD FR-4):

| Type | Role |
| --- | --- |
| `session_started` | Chat Session / turn stream begun |
| `reasoning` | Optional plan/thinking text |
| `token` | Answer text chunks |
| `tool_use` | Gateway Tool invoked (name + args as available) |
| `tool_result` | Tool finished (payload/summary as available) |
| `error` | Tool or agent failure surfaced to UI |
| `done` | Terminal event for the turn |

Payload JSON shapes, field names, and ordering guarantees are architecture/implementation decisions. If the runtime cannot emit `reasoning`, omit it; UI must tolerate absence.

## C. Memory mechanism options

PRD requires multi-turn within one session only. Candidate mechanisms (pick in architecture):

- AgentCore Memory
- DynamoDB-backed session store
- In-runtime session state for short demos

Cross-day resume / list UI explicitly deferred.

## D. Public API constraints (UX-relevant)

- **PubMed / NCBI E-utilities:** rate limits (commonly ~3 req/s without key); IDs are numeric PMIDs.
- **ClinicalTrials.gov:** NCT ID pattern `NCT` + 8 digits; paginated search; implement backoff on 429.
- **ChEMBL:** ChEMBL IDs (`CHEMBL` + number); throttling common without a dedicated key.

These constrain tool implementation and demo reliability; they are not separate product features.

## E. Competitive stance (brief-aligned)

Win on: time-to-pilot after CDK, streaming tool transparency, clean destroy, add-tool-in-a-day path.

Do not claim: proprietary KG, closed literature, clinical-grade ranking, replacement for experimental validation.

Named comps for context only: Open Targets, BenchSci, Biomni, FutureHouse.

## F. Disclaimer copy (approved for V1 UI)

> Research assistance only. Not medical advice. Verify claims against primary sources (PMID / NCT / ChEMBL IDs). Not for clinical decision-making.

## G. Canonical demo prompts (from README / brief)

1. What is the mechanism of action of Herceptin?
2. Which patient populations are most vulnerable to Herceptin cardiotoxicity?
3. How could Herceptin be modified to reduce cardiac binding? / safer targeting strategies

Patent-related README examples are **out of V1** (no USPTO tool).

## H. Deferred tool backlog (not V1 requirements)

OpenFDA, PubChem, UniProt, STRING, Ensembl, GTEx, GEO, Reactome, KEGG, PDB, AlphaFold, USPTO — README catalog items deferred; near-term preference after V1 is Open Targets–style structured evidence / pathway tools before multi-agent orchestration.

## I. Rejected for V1 PRD (explicit)

- Self-signup UI
- Federate/Midway SSO
- Session list / cross-day resume
- Tools 4–5 in the default deploy
- Production SLAs / on-call
- Heavy WAF/CI as acceptance gates

## J. Finalize dispositions (2026-07-25)

**Assumptions 1–7:** accepted as written; NFR-9 stall timeout set to soft **5 minutes**.

**Open Questions:** #2 resolved in PRD; #1, #3, #4, #5 → architecture / roadmap.

**Input reconciliation (non-blocking; no PRD content edits per owner):**

- Brief “3–5 tools” vs PRD “exactly 3” — intentional Discovery override (owner confirmed).
- Brief problem narrative / “governed / productized desk research” tone — carried sufficiently in Vision + Non-Goals; full problem essay left in brief.
- README multi-tool catalog / six-domain taxonomy / protein-interaction examples — intentional V1 deferral (addendum §H); “persistent sessions” clarified in PRD as in-session only.
- Gateway tool host as Lambda — mechanism for architecture (addendum §A path already shows Gateway → APIs).

**Reviewer gate:** rubric overall **strong**; 0 critical / 0 high. Medium/low findings deferred (observability smoke scenario, FR-12 negative probes, error-event shape canonicalization) → architecture / story refinement. See `review-rubric.md`.

## K. Local specialist agent suite (2026-07-26 Fast-path addendum)

**Intent:** Spec domain behavior for local-only specialist packages scaffolded to match sample `agents/` layout—without reopening V1 platform scope or multi-agent Runtime.

**Production path unchanged:** Cloud demo / FR-1–FR-21 remain on **Unified Research Agent** only (single Runtime). Specialists and supervisor are **not** CDK/AgentCore deliverables in V1.

**Shared constraints (all LA agents):**

| Constraint | Rule |
| --- | --- |
| Tools allowed | Exactly V1 three: `pubmed`, `clinicaltrials`, `chembl` (via `agents/framework` → unified-research-agent adapters / Gateway client) |
| Boundary | Research assistance only; not medical advice; not clinical decision-making (same as Disclaimer / FR-12) |
| Deploy | **Out of scope:** no new AgentCore Runtime, no new CDK stacks, no Gateway changes for specialists |
| Packaging | Package + domain system prompt + local-run README; share `agents/framework/` |
| Code origin | Rewrite domain prompts from sample *intent*; do not copy proprietary sample implementations |

**Cross-cutting local FRs**

| ID | Requirement |
| --- | --- |
| LA-FR-0 | Specialists reuse shared framework helpers and V1 tools; no private tool clients |
| LA-FR-8 | Docs (`agents/README.md`) state: specialists/supervisor/genetic = local; production = unified-research-agent only |
| LA-FR-9 | Unified Research Agent system prompt consolidates the five specialist domains for the cloud path (single agent) |

### K.1 Drug Profile Analysis Agent (`drug-profile-analysis-agent`)

- **Purpose:** MoA, toxicity signals, high-level PK context from public evidence.
- **Example queries:** “What is the mechanism of action of Herceptin?” · “What toxicity signals are reported for trastuzumab in public literature?”
- **Success ACs:** Local CLI runs; uses ≥1 V1 tool when answering evidence questions; cites tool IDs when present; refuses actionable dosing; research-assist framing.
- **Out of scope:** Runtime/CDK deploy; OpenFDA as a required tool.

### K.2 Patient Risk Assessment Agent (`patient-risk-assessment-agent`)

- **Purpose:** Population / vulnerability / biomarker signals from public literature and trials (research framing).
- **Example queries:** “Which patient populations are most vulnerable to its cardiotoxicity?” · “What trial populations are commonly studied for trastuzumab cardiac risk?”
- **Success ACs:** Local CLI runs; prefers pubmed/clinicaltrials; no patient-specific care plans; research-assist boundary held.
- **Out of scope:** Runtime/CDK; FAERS/OpenFDA as required tools; clinical risk scores for individuals.

### K.3 Pathway Mapping Agent (`pathway-mapping-agent`)

- **Purpose:** Pathway / interaction context for target-ID questions within V1 tool limits.
- **Example queries:** “What pathways are implicated in HER2 signaling based on public literature?” · “How does trastuzumab relate to HER2 pathway nodes in published reviews?”
- **Success ACs:** Local CLI runs; uses pubmed (and other V1 tools if relevant); **states limits** when STRING/Reactome/KEGG are unavailable; does not invent pathway DB IDs.
- **Out of scope:** Runtime/CDK; dedicated pathway Gateway tools (deferred backlog §H).

### K.4 Cardioprotection Target Agent (`cardioprotection-target-agent`)

- **Purpose:** Cardiac safety / cardioprotection / cardiotoxicity research hypotheses.
- **Example queries:** “What cardioprotective strategies are discussed alongside HER2-targeted therapy in literature?” · “Summarize public evidence on trastuzumab-related cardiac risk mechanisms.”
- **Success ACs:** Local CLI runs; pubmed/clinicaltrials primary; no clinical monitoring/dosing instructions; research-assist boundary held.
- **Out of scope:** Runtime/CDK; GTEx/HPA/UniProt as required tools.

### K.5 Drug Design Hypothesis Agent (`drug-design-hypothesis-agent`)

- **Purpose:** Chemistry / safer-targeting / optimization hypotheses grounded in chembl + literature.
- **Example queries:** “How could Herceptin be modified to reduce cardiac binding?” · “What ChEMBL bioactivity context exists for HER2-targeted agents relevant to selectivity?”
- **Success ACs:** Local CLI runs; uses chembl and/or pubmed; does not invent docking/PDB results; research-assist boundary held.
- **Out of scope:** Runtime/CDK; PDB/docking Gateway tools as required.

### K.6 Medical Supervisor Agent (`medical-supervisor-agent`) — local stubs only

- **Purpose:** Local router/coordinator pattern for experimenting with agents-as-tools **in-process**.
- **Example queries:** Same canonical Herceptin set; expect routing or synthesis stubs, not cloud orchestration.
- **Success ACs:** Local CLI runs; README states **not** for AgentCore multi-agent deploy; may call specialist stubs in-process; research-assist boundary held.
- **Out of scope:** Multi-agent Runtime, supervisor IAM/Gateway, UI integration, production FR coverage.

### K.7 Genetic Risk Assessment (`genetic-risk-assessment`) — local only

- **Purpose:** Genetics / susceptibility literature framing (e.g. ERBB2 context) with V1 tools only.
- **Example queries:** “Summarize public literature on ERBB2 germline context in breast cancer research.” · “What genetic themes appear in trastuzumab response literature?”
- **Success ACs:** Local CLI runs; pubmed primary; no personal genetic counseling; states absence of Ensembl/GWAS Gateway tools.
- **Out of scope:** Runtime/CDK; Ensembl/GWAS Gateway targets.

### K.8 Stories / architecture pointers

- Local epic + stories: `_bmad-output/planning-artifacts/epics-local-specialists.md`
- Short architecture note: `_bmad-output/planning-artifacts/architecture/architecture-note-local-specialists-2026-07-26.md`

**[ASSUMPTION]** Specialist “done” for V1 means meeting LA ACs locally; cloud SM-1 continues to validate only unified-research-agent + platform FRs.

## L. Platform maturity backlog (2026-07-26 Fast-path)

**Intent:** Capture post-V1 platform/product maturity requirements as lightweight **PM-FRs** without expanding V1 FR-1–FR-21. Full story ACs live in `epics-platform-maturity.md`. Catalog/rationale: `roadmap-platform-maturity.md`.

**V1 unchanged:** Destroy-when-not-demoing, exactly three Gateway tools, no vector DB on hot path, no hard SLAs, baseline Cognito + Stream security remain.

### L.1 PM-FR index

| ID | Epic | Requirement (summary) |
| --- | --- | --- |
| PM-FR-1 | M1 | Golden-prompt eval suite (MoA, follow-up/risk, clinical refusal) with pass/fail report |
| PM-FR-2 | M1 | FR-12 negative probes fail the suite on actionable clinical orders |
| PM-FR-3 | M1 | CloudWatch dashboard for Stream + tool errors/duration |
| PM-FR-4 | M1 | Optional CloudWatch alarms (SNS/email); no on-call required |
| PM-FR-5 | M2 | OpenTelemetry (or X-Ray) traces Stream → Runtime → tools |
| PM-FR-6 | M2 | Custom metrics: turn latency, tool errors, tokens when available |
| PM-FR-7 | M2 | Alert→debug runbook (no 24×7 obligation) |
| PM-FR-8 | M2 | CloudTrail enablement documented at account level |
| PM-FR-9 | M2 | Bedrock/Lambda spend or budget alarms documented |
| PM-FR-10 | M3 | Written decision before any vector DB/RAG |
| PM-FR-11 | M3 | Optional RAG spike only if PM-FR-10 adopts; feature-flaggable |
| PM-FR-12 | M3 | Optional Gateway tool #4 under shared error/`ids` contract + eval coverage |
| PM-FR-13 | M4 | Staging environment + promote path |
| PM-FR-14 | M4 | Blue/green or traffic-shift for Runtime/UI with rollback docs |
| PM-FR-15 | M4 | SLOs for always-on envs only (not destroy-when-idle demos) |
| PM-FR-16 | M4 | Modest authenticated load/concurrency smoke |
| PM-FR-17 | M4 | EventBridge before Kafka; Kafka only with decision record |
| PM-FR-18 | M5 | Lightweight threat model (STRIDE-style) |
| PM-FR-19 | M5 | Optional CloudFront WAF managed rules |
| PM-FR-20 | M5 | Cognito SAML/OIDC federation spike path |
| PM-FR-21 | M5 | Secrets Manager pattern for future API keys |
| PM-FR-22 | M5 | Honest HA/multi-AZ expectations (no false product SLAs) |

### L.2 Pointers

- Epics + stories: `_bmad-output/planning-artifacts/epics-platform-maturity.md`
- Roadmap ladder: `_bmad-output/planning-artifacts/roadmap-platform-maturity.md`
- Architecture note: `_bmad-output/planning-artifacts/architecture/architecture-note-platform-maturity-2026-07-26.md`
- Backlog story files: `_bmad-output/implementation-artifacts/stories/M*.md`

**[ASSUMPTION]** Starting any M\* epic is optional and does not reopen V1 acceptance; SM-1…SM-5 remain the V1 bar.
