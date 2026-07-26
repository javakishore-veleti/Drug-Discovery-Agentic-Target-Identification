# Genetic Risk Assessment Agent (local only)

Specialist research-assist agent. **Not deployed** to AgentCore Runtime — production uses `unified-research-agent` only.

## Run

```bash
cd agents/genetic-risk-assessment
PYTHONPATH=.. python -m genetic_risk_assessment "Your research question"
```

Optional env: reuse `../unified-research-agent/.env` (`BEDROCK_MODEL_ID`, `AGENTCORE_GATEWAY_URL`).

Tools: `pubmed`, `clinicaltrials`, `chembl` via `agents/framework`.
