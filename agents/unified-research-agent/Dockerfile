# AgentCore Runtime image (Story 3.1) — linux/arm64 required by AgentCore.
# Build context: repository root (see infra/backend Runtime stack).
FROM --platform=linux/arm64 public.ecr.aws/docker/library/python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/agents/unified-research-agent \
    BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-6 \
    AWS_DEFAULT_REGION=us-east-1 \
    USE_GATEWAY_TOOLS=true
# AGENTCORE_MEMORY_ID is injected by CDK Runtime (Story 3.2); do not alias MEMORY_ID.

COPY agents/unified-research-agent/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# Preserve repo layout so unified_research_agent.paths finds gateways/database.
COPY agents/unified-research-agent/unified_research_agent \
    /app/agents/unified-research-agent/unified_research_agent
COPY gateways/database /app/gateways/database

WORKDIR /app/agents/unified-research-agent

EXPOSE 8080

# AgentCore Runtime HTTP contract: /invocations + /ping on 8080
CMD ["uvicorn", "unified_research_agent.runtime_app:app", "--host", "0.0.0.0", "--port", "8080"]
