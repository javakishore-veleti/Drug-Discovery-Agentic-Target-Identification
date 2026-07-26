# Cardioprotection Target Agent (local only)

Specialist research-assist agent. **Not deployed** to AgentCore Runtime — production uses `unified-research-agent` only.

## Run

```bash
cd agents/cardioprotection-target-agent
PYTHONPATH=.. python -m cardioprotection_target_agent "Your research question"
```

Optional env: reuse `../unified-research-agent/.env` (`BEDROCK_MODEL_ID`, `AGENTCORE_GATEWAY_URL`).

Tools: `pubmed`, `clinicaltrials`, `chembl` via `agents/framework`.
