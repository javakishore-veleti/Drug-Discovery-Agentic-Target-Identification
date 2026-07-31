# Agents layout

## Production (cloud)

| Package | Role |
| --- | --- |
| [`unified-research-agent/`](./unified-research-agent/) | **Only** AgentCore Runtime agent. Consolidates five research domains + V1 tools (`pubmed`, `clinicaltrials`, `chembl`). Deployed via CDK Runtime stack. |

## Local-only specialists (not Runtime)

Domain CLIs that reuse `framework/` + the same V1 tools. **Do not deploy** as separate AgentCore Runtimes for V1.

With `VITE_STACK_MODE=local`, the web UI agent dropdown posts `agentId` to `local/stream_app.py`, which loads the matching factory from `local/agent_registry.py`. AWS / CloudFront stays unified-only.

| Package | Focus |
| --- | --- |
| [`drug-profile-analysis-agent/`](./drug-profile-analysis-agent/) | MoA / toxicity / PK context |
| [`patient-risk-assessment-agent/`](./patient-risk-assessment-agent/) | Population / risk signals |
| [`pathway-mapping-agent/`](./pathway-mapping-agent/) | Pathway / network literature framing |
| [`cardioprotection-target-agent/`](./cardioprotection-target-agent/) | Cardiac safety / cardioprotection |
| [`drug-design-hypothesis-agent/`](./drug-design-hypothesis-agent/) | Design / chemistry hypotheses |

## Local-only extras (stubs)

| Package | Role |
| --- | --- |
| [`medical-supervisor-agent/`](./medical-supervisor-agent/) | Local router with in-process specialist stubs — **no** multi-agent Runtime |
| [`genetic-risk-assessment/`](./genetic-risk-assessment/) | Local genetics research framing (V1 tools only) |

## Shared

| Package | Role |
| --- | --- |
| [`framework/`](./framework/) | Config, research-assist boundary, tool wiring, Strands factory, CLI helper |

## Quick local run

```bash
cd agents/drug-profile-analysis-agent
PYTHONPATH=.. python -m drug_profile_analysis_agent "What is the mechanism of action of Herceptin?"
```

All agents: research assistance only — not medical advice / not clinical decision-making.
