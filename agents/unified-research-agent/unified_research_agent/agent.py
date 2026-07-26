"""Create the local Unified Research Agent (Story 1.1 — no tools yet)."""

from __future__ import annotations

from strands import Agent
from strands.models import BedrockModel

from .config import get_aws_region, get_bedrock_model_id


def create_agent() -> Agent:
    """Build a Strands Agent backed by the pinned Bedrock model."""
    model = BedrockModel(
        model_id=get_bedrock_model_id(),
        region_name=get_aws_region(),
    )
    return Agent(model=model)
