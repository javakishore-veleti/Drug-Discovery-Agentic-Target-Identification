# Gateway tool #4 — Open Targets (Story M3.3)

**Status:** implemented · Default deploy remains **exactly 3** tools (FR-16).  
Enable with CDK: `-c enableTool4=true`.

## Recommendation

| Rank | Candidate | Why | Cost / risk |
| --- | --- | --- | --- |
| 1 | **Open Targets** (or Target Validation Platform API) | Structured target–disease evidence; fills “validated target” gap without claiming clinical-grade ranking | Public API; new Lambda + adapter |
| 2 | **UniProt** | Protein identity / function for HER2-style questions | Simple REST; overlaps PubMed narrative |
| 3 | USPTO | Patent narrative from sample README | Needs API key → Secrets Manager (M5.4) |

**Pick for first implementation:** Open Targets–style evidence tool named logically `opentargets` (or `uniprot` if OT access is awkward).

## Contract (must match V1 tools)

- Logical MCP name allowlisted only when `-c enableTool4=true` (default **off**).
- Result shape: `status`, `tool`, `ids` (new key e.g. `ids.ensembl` or `ids.uniprot`), `summary` / `message` on error.
- Timeout ≤ 45s; 429 backoff; safe `status: error` (no secrets/stack traces).
- Shared under `gateways/database/<tool>/`.
- Eval: add one golden case in `evals/golden_prompts.json` when enabled.

## Non-goals

- Do not enable tool #4 in default demo destroy-when-idle path until evals pass.
- Do not add vector/RAG for this (M3.1 / M3.2 blocked).

## Next implementation steps

1. Adapter + Lambda handler + unit smoke against public API.
2. Gateway CDK target behind context flag; Runtime env unchanged when off.
3. Agent tool registration when flag on.
4. `docs/evals.md` case + SM update.
