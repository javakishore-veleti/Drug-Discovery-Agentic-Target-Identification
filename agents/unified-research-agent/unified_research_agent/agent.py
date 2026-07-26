"""Create the local Unified Research Agent (Stories 1.1–1.2)."""

from __future__ import annotations

from strands import Agent
from strands.models import BedrockModel

from .config import get_aws_region, get_bedrock_model_id
from .prompts import RESEARCH_ASSIST_SYSTEM_PROMPT


def create_agent() -> Agent:
    """Build a Strands Agent with pinned Bedrock model + research-assist prompt."""
    model = BedrockModel(
        model_id=get_bedrock_model_id(),
        region_name=get_aws_region(),
    )
    return Agent(
        model=model,
        system_prompt=RESEARCH_ASSIST_SYSTEM_PROMPT,
    )
