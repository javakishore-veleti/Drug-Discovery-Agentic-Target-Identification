"""Local supervisor agent — specialist stubs + optional direct V1 tools."""

from __future__ import annotations

from strands import Agent

from framework.base_agent import create_research_agent
from framework.tools import V1_TOOLS

from .prompts import SYSTEM_PROMPT
from .specialist_stubs import SPECIALIST_STUB_TOOLS


def create_agent() -> Agent:
    # Local only: supervisor tools = specialist stubs + shared evidence tools.
    return create_research_agent(
        SYSTEM_PROMPT,
        tools=[*SPECIALIST_STUB_TOOLS, *V1_TOOLS],
    )
