# Unified Research Agent (local)

Local Strands + Amazon Bedrock entrypoint for **Agentic Target ID** V1.

Story **1.1** scope: runnable package with pinned `BEDROCK_MODEL_ID`. No Gateway, Stream Lambda, Cognito, or React UI.

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
| `BEDROCK_MODEL_ID` | `us.anthropic.claude-sonnet-4-20250514-v1:0` | Architecture AD-6 pin |
| `AWS_REGION` | `us-east-1` | Or `AWS_DEFAULT_REGION` |

If Sonnet 4 is not enabled in your account, set the AD-6 fallback in `.env`:

```bash
BEDROCK_MODEL_ID=anthropic.claude-3-7-sonnet-20250219-v1:0
```

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
    └── agent.py         # Strands Agent factory
```

## Out of scope (later stories)

- Research-assist system prompt (1.2)
- PubMed / Gateway tools (1.3+, Epic 2)
- AgentCore Runtime, Stream Lambda, Cognito, React UI
