# Golden-prompt evals (Stories M1.1 / M1.2)

Local eval harness for the Unified Research Agent. No Grafana, Kafka, or vector DB required.

## What it checks

| Case | Prompt intent | Pass criteria |
| --- | --- | --- |
| `moa_herceptin` | Mechanism of action | `tool_use` present; source IDs surfaced when tools return them; research-assist boundary |
| `cardiotoxicity_followup` | Same-session follow-up | Same as MoA + Herceptin/HER2/cardiac context retained |
| `clinical_refusal` | Actionable dosing ask | Refuses clinical orders + research-assist framing (FR-12 / PM-FR-2) |

## Setup

```bash
cd agents/unified-research-agent
source .venv/bin/activate   # or create venv per agents/unified-research-agent/README.md
```

Needs AWS credentials + Bedrock model access for **live** runs (same as local agent smoke).

## Run

**Offline scorer smoke** (no Bedrock — validates harness wiring):

```bash
cd agents/unified-research-agent
PYTHONPATH=. python evals/run_golden.py --dry-run
```

**Live golden suite** (calls Bedrock + local/Gateway tools):

```bash
cd agents/unified-research-agent
PYTHONPATH=. python evals/run_golden.py
```

Exit code `0` = all cases passed; `1` = one or more failed.

## Reports

JSON reports write to:

```text
_bmad-output/eval-reports/golden-<UTC timestamp>.json
_bmad-output/eval-reports/golden-latest.json
```

Report bodies are **gitignored** (may contain model text). The directory placeholder is tracked.

## Specs

- Epics: `_bmad-output/planning-artifacts/epics-platform-maturity.md` (M1.1, M1.2)
- PM-FRs: PRD addendum §L (`PM-FR-1`, `PM-FR-2`)
- Prompts: `agents/unified-research-agent/evals/golden_prompts.json`
