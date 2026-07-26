# Medical Supervisor Agent (local stub only)

Local router/coordinator that can call in-process specialist stubs (“agents as tools” for experimentation).

**Not deployed** to AgentCore Runtime. V1 production is a **single** `unified-research-agent` — do not add supervisor/multi-agent cloud stacks for this pilot.

## Run

```bash
cd agents/medical-supervisor-agent
PYTHONPATH=.. python -m medical_supervisor_agent "What is the mechanism of action of Herceptin?"
```
