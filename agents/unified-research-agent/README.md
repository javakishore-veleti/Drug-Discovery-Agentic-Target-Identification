# Unified Research Agent (local)

Local Strands + Amazon Bedrock entrypoint for **Agentic Target ID** V1.

Stories **1.1–1.4** (Epic 1), **2.1–2.4** (Gateway three tools), **3.1** (AgentCore Runtime container): pinned model, research-assist prompt, evidence tools via Gateway MCP when configured. Memory / Stream / Cognito UI later.

## Prerequisites

- Python **3.12+**
- AWS credentials configured (CLI profile or environment)
- Amazon Bedrock **model access** enabled in the target region for the pinned model

## Setup

```bash
cd agents/unified-research-agent
python3.12 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # edit if needed
```

## Configuration

| Variable | Default | Notes |
| --- | --- | --- |
| `BEDROCK_MODEL_ID` | `us.anthropic.claude-sonnet-4-6` | Active US pin (AD-6 intent; Sonnet 4.0 id is Legacy/EOL) |
| `AWS_REGION` | `us-east-1` | Or `AWS_DEFAULT_REGION` |
| `AGENTCORE_GATEWAY_URL` | _(unset)_ | Gateway MCP URL from `infra/backend` deploy |
| `USE_GATEWAY_TOOLS` | auto | Default on when Gateway URL is set; `false` forces local adapter |

If Sonnet 4.6 is not enabled, set the fallback in `.env`:

```bash
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0
```

Enable model access in Bedrock console for the chosen id. Older pins such as `claude-sonnet-4-20250514` / `claude-3-7-sonnet` may return Legacy/EOL errors.

## Research-assist boundary (Story 1.2)

The agent loads a system prompt (`unified_research_agent/prompts.py`) that enforces research assistance only — not medical advice / not clinical decision-making — aligned with the PRD Disclaimer.

Quick check (with AWS creds + model access):

```bash
PYTHONPATH=. python -m unified_research_agent \
  "What dose of Herceptin should I prescribe my patient today?"
```

Expect a refusal of actionable clinical dosing plus research-only framing.

## PubMed tool (Story 1.3)

Shared adapter: `gateways/database/pubmed/adapter.py` (reuse later for Gateway Lambda).  
Local Strands tool name: `pubmed`. OK results include `ids.pmid` (string array). Errors use `status: error` within a **45s** wall-clock budget (429 backoff included).

Adapter-only smoke (no Bedrock):

```bash
# from repo root
PYTHONPATH=gateways/database python -c "
from pubmed.adapter import search_pubmed
r = search_pubmed('trastuzumab mechanism of action', retmax=5)
print(r['status'], r['ids']['pmid'][:5], r.get('message'))
"
```

Agent + tool (needs Bedrock):

```bash
PYTHONPATH=. python -m unified_research_agent \
  "Use the pubmed tool to find literature on the mechanism of action of Herceptin (trastuzumab). List PMIDs."
```

## Story 1.4 — Herceptin synthesis smoke

```bash
cd agents/unified-research-agent
source .venv/bin/activate
PYTHONPATH=. python -m unified_research_agent \
  "What is the mechanism of action of Herceptin?"
```

Expect: `pubmed` tool use, a short synthesis, and at least one `PMID …` from the tool’s `ids.pmid` in the answer.

## Run (trivial smoke)

From this directory (with venv active):

```bash
PYTHONPATH=. python -m unified_research_agent
```

Or with an explicit prompt:

```bash
PYTHONPATH=. python -m unified_research_agent "Say hello in one short sentence."
```

On success you should see `BEDROCK_MODEL_ID=...` on stderr and a model reply on stdout.

## Layout

```text
agents/unified-research-agent/
├── README.md
├── requirements.txt
├── .env.example
└── unified_research_agent/
    ├── __init__.py
    ├── __main__.py      # CLI entrypoint
    ├── config.py        # BEDROCK_MODEL_ID / region
    ├── prompts.py       # Research-assist system prompt (FR12 / AD-14)
    ├── paths.py         # Import path to gateways/database
    ├── agent.py         # Strands Agent factory
    └── tools/
        └── pubmed_tool.py
```

Shared (repo):

```text
gateways/database/pubmed/
├── __init__.py
└── adapter.py           # NCBI E-utilities client + normalized ids shape
```

## Gateway PubMed (Story 2.1)

Deploy Gateway + PubMed Lambda (see `infra/backend/README.md`), then:

```bash
# in agents/unified-research-agent/.env
AGENTCORE_GATEWAY_URL=https://..../mcp
USE_GATEWAY_TOOLS=true
```

```bash
pip install -r requirements.txt
PYTHONPATH=. python -m unified_research_agent --list-gateway-tools
# expect: logical_tools=pubmed

PYTHONPATH=. python -m unified_research_agent \
  "Use the pubmed tool to find literature on trastuzumab mechanism. List PMIDs."
```

Agent tool name stays exactly `pubmed`. When Gateway is enabled, invocations go through AgentCore Gateway MCP (SigV4) into the shared Lambda adapter — not the local-only path.

## Gateway ClinicalTrials (Story 2.2)

Logical MCP tool: `clinicaltrials`. OK results include `ids.nct` (`NCT` + 8 digits).

```bash
PYTHONPATH=. python -m unified_research_agent --list-gateway-tools
# expect: logical_tools includes clinicaltrials

PYTHONPATH=gateways/database python -c "
from clinicaltrials.adapter import search_clinicaltrials
r = search_clinicaltrials('trastuzumab HER2', retmax=5)
print(r['status'], r['ids']['nct'][:5], r.get('message'))
"
```

## Gateway ChEMBL (Story 2.3)

Logical MCP tool: `chembl`. OK results include `ids.chembl` (`CHEMBL` + digits).

```bash
PYTHONPATH=gateways/database python -c "
from chembl.adapter import search_chembl
r = search_chembl('trastuzumab', retmax=5)
print(r['status'], r['ids']['chembl'][:5], r.get('message'))
"
```

## Epic 2 complete (Story 2.4)

Exactly three Gateway tools + shared error contract — see [`docs/tool-result-contract.md`](../../docs/tool-result-contract.md).

```bash
PYTHONPATH=. python -m unified_research_agent --list-gateway-tools
# expect: logical_tools=chembl,clinicaltrials,pubmed  (exit 0 only if exact set)

PYTHONPATH=. python -m unified_research_agent --smoke-epic2
# exact V1 tools + forced empty-query errors + post-failure agent turn
```

## AgentCore Runtime + Memory (Stories 3.1–3.2)

ARM64 Docker image + FastAPI `/invocations` + `/ping` — see [`docs/runtime.md`](../../docs/runtime.md).

```bash
# build from repo root
docker buildx build --platform linux/arm64 \
  -f agents/unified-research-agent/Dockerfile -t agentic-target-id-ura:local --load .
```

CDK: `infra/backend` stack `AgenticTargetIdRuntime` sets `BEDROCK_MODEL_ID`,
`AGENTCORE_GATEWAY_URL`, and `AGENTCORE_MEMORY_ID` (STM; no `MEMORY_ID` alias).

Two-turn Memory smoke (same Runtime session key):

```bash
export AGENT_RUNTIME_ARN=...
python scripts/smoke_runtime_memory_two_turn.py
```

## Out of scope (later stories)

- Herceptin multi-turn Runtime smoke (Story 3.3)
- Stream Lambda, Cognito, React UI (Epics 4–5)
