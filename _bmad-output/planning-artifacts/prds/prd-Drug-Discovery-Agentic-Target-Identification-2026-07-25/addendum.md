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
