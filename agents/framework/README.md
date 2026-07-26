# `agents/framework` — shared local helpers

Lightweight equivalent of a sample “BaseAgent” layer for **this** repo:

| Module | Role |
| --- | --- |
| `config.py` | `BEDROCK_MODEL_ID`, region, optional `AGENTCORE_GATEWAY_URL` |
| `prompts.py` | Shared research-assist / not-medical-advice boundary |
| `tools.py` | Reuses `unified-research-agent` V1 tools (`pubmed`, `clinicaltrials`, `chembl`) |
| `base_agent.py` | `create_research_agent` / `run_prompt` (Strands + Bedrock) |
| `cli.py` | Shared local CLI runner |

**Not** a cloud deploy framework — no Runtime packaging, no supervisor Gateway wiring here.

## Usage

Specialist packages call:

```python
from framework.base_agent import create_research_agent
from framework.prompts import with_research_assist_boundary
```

Ensure `agents/` is on `PYTHONPATH` (see each agent README).
