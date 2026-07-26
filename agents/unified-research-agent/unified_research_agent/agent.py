"""Create the Unified Research Agent (Stories 1.1–3.2)."""

from __future__ import annotations

from typing import Any

from strands import Agent
from strands.models import BedrockModel

from .config import get_aws_region, get_bedrock_model_id
from .prompts import RESEARCH_ASSIST_SYSTEM_PROMPT
from .tools import chembl_search, clinicaltrials_search, pubmed_search


def create_agent(*, session_manager: Any | None = None) -> Agent:
    """
    Build a Strands Agent with Bedrock model, research-assist prompt, and tools.

    When AGENTCORE_GATEWAY_URL is set (and USE_GATEWAY_TOOLS is not false),
    `pubmed` / `clinicaltrials` / `chembl` invoke AgentCore Gateway MCP.

    When ``session_manager`` is provided (Story 3.2), turns persist to AgentCore
    Memory STM for that Chat Session key.
    """
    model = BedrockModel(
        model_id=get_bedrock_model_id(),
        region_name=get_aws_region(),
    )
    kwargs: dict[str, Any] = {
        "model": model,
        "system_prompt": RESEARCH_ASSIST_SYSTEM_PROMPT,
        "tools": [pubmed_search, clinicaltrials_search, chembl_search],
    }
    if session_manager is not None:
        kwargs["session_manager"] = session_manager
    return Agent(**kwargs)
