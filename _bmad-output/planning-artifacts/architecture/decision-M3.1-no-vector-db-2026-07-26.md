# Decision record — M3.1 Retrieval / vector DB

**Status:** ADOPTED (default) · **Date:** 2026-07-26  
**Story:** M3.1 · **PM-FR-10**

## Decision

**Do not add a vector database or RAG hot path for V1 / near-term V1.5.**

Evidence remains **live public API tools** via AgentCore Gateway (`pubmed`, `clinicaltrials`, `chembl`).

## Context

- V1 PRD / AD spine: no proprietary corpus; no vector DB on hot path.
- README marketing catalog of many DBs is intentionally deferred (addendum §H).
- Adding OpenSearch/pgvector without a owned corpus creates cost and false precision.

## Consequences

- Story **M3.2** (vector spike) stays **blocked / cancelled** until this record is superseded.
- Story **M3.3** (tool #4) may proceed independently of RAG.
- If a private non-PHI corpus appears later, write a new decision that names: corpus owner, refresh, PII rules, engine choice, and success metric — then reopen M3.2.

## Alternatives considered

| Option | Why not now |
| --- | --- |
| Embed PubMed abstracts locally | Licensing/refresh/cost; NCBI live search already covers MoA demo |
| OpenSearch Serverless | Idle cost fights destroy-when-idle model |
| pgvector on RDS | New always-on data plane for a pilot |

## Supersede

Replace this file (or add `decision-M3.1-adopt-rag-….md` with `ADOPTED`) before implementing M3.2.
