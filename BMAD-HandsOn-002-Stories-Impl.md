# BMAD Hands-On

## Step - 24 My Reply
```text
[C] Complete Workflow

Close planning. Commit epics.md and related planning artifacts if not already committed.
Then start Story 1.1: Scaffold agent package + pinned Bedrock model.
```

## Step - 24 Cursor Reply
```text
Planning closed. Epics committed and pushed as e3b0d7b.

Story 1.1 implemented (not committed yet — say if you want that).

Package
agents/unified-research-agent/

requirements.txt — strands-agents ^1.47, boto3, dotenv
.env.example — BEDROCK_MODEL_ID pin + AD-6 fallback
unified_research_agent/config.py — reads BEDROCK_MODEL_ID / region
unified_research_agent/agent.py — Strands + BedrockModel
unified_research_agent/__main__.py — CLI entrypoint
README.md — install + run
Verify locally
cd agents/unified-research-agent
source .venv/bin/activate   # already created in this env
cp .env.example .env
PYTHONPATH=. python -m unified_research_agent
Config/import/--help checked here. Live Bedrock call needs your AWS creds + model access.

Next when you’re ready: commit Story 1.1, then Story 1.2 (research-assist system prompt).
```

## Step - 25 My Reply
```text
Good progress — commit Story 1.1 before starting 1.2.

Then start Story 1.2 (research-assist system prompt) in that same chat.

Optional: after 1.1 smoke, confirm Sonnet 4 is enabled; if invoke fails, switch .env to the AD-6 Haiku/3.7 fallback and note it in the README.
```

## Step - 25 Cursor Reply
```text
```

## Step - 26 My Reply
```text

```