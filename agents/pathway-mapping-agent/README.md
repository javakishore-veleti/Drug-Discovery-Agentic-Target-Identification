# Pathway Mapping Agent (local only)

Specialist research-assist agent. **Not deployed** to AgentCore Runtime — production uses `unified-research-agent` only.

## Run

```bash
cd agents/pathway-mapping-agent
PYTHONPATH=.. python -m pathway_mapping_agent "Your research question"
```

Optional env: reuse `../unified-research-agent/.env` (`BEDROCK_MODEL_ID`, `AGENTCORE_GATEWAY_URL`).

Tools: `pubmed`, `clinicaltrials`, `chembl` via `agents/framework`.
