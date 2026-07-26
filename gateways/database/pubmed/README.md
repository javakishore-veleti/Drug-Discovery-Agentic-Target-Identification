# PubMed adapter + Gateway Lambda

Shared NCBI E-utilities client for Agentic Target ID.

- Used by local Strands tool (`agents/unified-research-agent`)
- Reused by AgentCore Gateway Lambda (`handler.py`) — Story 2.1
- Same `search_pubmed` + `ids` shape (no duplicated search logic)

## Result contract

```json
{
  "status": "ok" | "error",
  "tool": "pubmed",
  "ids": { "pmid": ["..."], "nct": [], "chembl": [] },
  "summary": "...",
  "articles": [{ "pmid": "...", "title": "..." }],
  "message": "..." 
}
```

`message` is set on `status: "error"`. Wall-clock timeout default **45s**; HTTP 429 retries with backoff.
