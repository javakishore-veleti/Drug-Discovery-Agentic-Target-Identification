# Unified Research Agent (local)

Local Strands + Amazon Bedrock entrypoint for **Agentic Target ID** V1.

Stories **1.1–1.4** (Epic 1 complete): pinned model, research-assist prompt, local PubMed tool, Herceptin synthesis with PMID surfacing. No AgentCore Gateway deploy, Stream Lambda, Cognito, or React UI yet.

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

## Out of scope (later stories)

- AgentCore Gateway deploy for all three tools (Epic 2)
- AgentCore Runtime, Stream Lambda, Cognito, React UI (Epics 3–5)
- AgentCore Runtime, Stream Lambda, Cognito, React UI
