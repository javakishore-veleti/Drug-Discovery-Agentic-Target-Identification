"""Create the Unified Research Agent (Stories 1.1–2.1)."""

from __future__ import annotations

from strands import Agent
from strands.models import BedrockModel

from .config import get_aws_region, get_bedrock_model_id
from .prompts import RESEARCH_ASSIST_SYSTEM_PROMPT
from .tools import chembl_search, clinicaltrials_search, pubmed_search


def create_agent() -> Agent:
    """
    Build a Strands Agent with Bedrock model, research-assist prompt, and tools.

    When AGENTCORE_GATEWAY_URL is set (and USE_GATEWAY_TOOLS is not false),
    `pubmed` / `clinicaltrials` / `chembl` invoke AgentCore Gateway MCP.
    """
    model = BedrockModel(
        model_id=get_bedrock_model_id(),
        region_name=get_aws_region(),
    )
    return Agent(
        model=model,
        system_prompt=RESEARCH_ASSIST_SYSTEM_PROMPT,
        tools=[pubmed_search, clinicaltrials_search, chembl_search],
    )
