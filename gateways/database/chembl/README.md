# ChEMBL adapter + Gateway Lambda

Shared ChEMBL Data Web Services client for Agentic Target ID (Story 2.3).

- Gateway Lambda: `handler.py` → MCP tool `chembl`
- Same normalized `ids` shape as PubMed / ClinicalTrials (AD-9); 45s budget + 429 backoff (AD-15)

## Result contract

```json
{
  "status": "ok" | "error",
  "tool": "chembl",
  "ids": { "pmid": [], "nct": [], "chembl": ["CHEMBL1201585"] },
  "summary": "...",
  "molecules": [{ "chembl": "...", "name": "...", "molecule_type": "..." }],
  "message": "..."
}
```

`ids.chembl` values match `CHEMBL` + digits when present.
