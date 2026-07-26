# ClinicalTrials.gov adapter + Gateway Lambda

Shared ClinicalTrials.gov API v2 client for Agentic Target ID (Story 2.2).

- Gateway Lambda: `handler.py` → MCP tool `clinicaltrials`
- Same normalized `ids` shape as PubMed (AD-9); 45s budget + 429 backoff (AD-15)

## Result contract

```json
{
  "status": "ok" | "error",
  "tool": "clinicaltrials",
  "ids": { "pmid": [], "nct": ["NCT01234567"], "chembl": [] },
  "summary": "...",
  "studies": [{ "nct": "...", "title": "...", "status": "..." }],
  "message": "..."
}
```

`ids.nct` values match `NCT` + 8 digits when present.
