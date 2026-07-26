# Architecture note — Local specialist agents (2026-07-26)

**Status:** note (not a full spine revision)  
**Binds:** PRD addendum §K · Epic L · `agents/README.md`

## Decision

Specialist packages under `agents/*` are **local CLI experiment surfaces**. They share:

- `agents/framework/` — config, research-assist boundary, Strands factory, CLI helper  
- V1 tools from `unified-research-agent` (`pubmed`, `clinicaltrials`, `chembl`) — local adapters or Gateway MCP when configured  

**Production Runtime remains a single agent:** `agents/unified-research-agent` (AD-2). No multi-Runtime, no supervisor Gateway, no new CDK stacks for specialists in V1.

## Explicit non-decisions (deferred)

- Agents-as-tools orchestration on AgentCore  
- Per-domain pathway/genetic Gateway tools (STRING, Ensembl, etc.)  
- UI routing to specialists  

## Implication

Invest in specialist prompts only against Epic L ACs. Cloud demos and FR coverage stay on unified + Epics 1–6.
