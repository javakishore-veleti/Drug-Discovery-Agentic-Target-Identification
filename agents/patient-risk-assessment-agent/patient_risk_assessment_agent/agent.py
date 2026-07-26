"""Create the local Patient Risk Assessment Agent."""

from __future__ import annotations

from strands import Agent

from framework.base_agent import create_research_agent
from .prompts import SYSTEM_PROMPT


def create_agent() -> Agent:
    return create_research_agent(SYSTEM_PROMPT)
