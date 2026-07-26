# Shared Gateway tool result contract (Epic 2 / AD-8 / AD-9 / AD-15)

All V1 AgentCore Gateway tools (`pubmed`, `clinicaltrials`, `chembl`) return the same top-level JSON shape so Stream Events can map `tool_result` uniformly later.

## V1 tool set (AD-3 / FR-16)

Default Gateway deploy exposes **exactly** these logical MCP names:

| Logical name | Wire name (typical) | `ids` key filled on success |
| --- | --- | --- |
| `pubmed` | `pubmed___pubmed` | `ids.pmid` |
| `clinicaltrials` | `clinicaltrials___clinicaltrials` | `ids.nct` |
| `chembl` | `chembl___chembl` | `ids.chembl` |

Agent code normalizes `${target}___${tool}` → logical name. Do not add a fourth tool without a deliberate FR/AD change.

## Result object

```json
{
  "status": "ok" | "error",
  "tool": "pubmed" | "clinicaltrials" | "chembl",
  "ids": {
    "pmid": ["..."],
    "nct": ["NCT01234567"],
    "chembl": ["CHEMBL25"]
  },
  "summary": "short text for the agent (may be empty on error)",
  "message": "present on error only — safe, no secrets/stack traces"
}
```

Optional detail arrays (tool-specific, ignored by ID surfacing):

- `pubmed`: `articles: [{pmid, title}, ...]`
- `clinicaltrials`: `studies: [{nct, title, status}, ...]`
- `chembl`: `molecules: [{chembl, name, molecule_type}, ...]`

### Rules

1. **`status: ok`** — always include top-level `ids` with all three keys (empty arrays when none). Agent cites IDs from `ids` only (AD-9).
2. **`status: error`** — include `tool`, short `message`, and empty `ids` arrays. Suitable for Stream `tool_result` + `error` events (AD-8).
3. **Resilience (AD-15)** — HTTP 429 backoff/retry; wall-clock budget ≤ **45s** then error (no hang).
4. **Session continuity (AD-8)** — a tool failure must not require redeploy; the agent accepts another turn in the same process/session.

## Forced failure (smoke)

Empty `query` (or `timeout_seconds` ≤ 0 / expired budget) yields `status: error` with a short message — used by Epic 2 smoke without calling public APIs unsuccessfully for long.

```bash
cd agents/unified-research-agent
PYTHONPATH=. python -m unified_research_agent --smoke-epic2
```
