"""Strands agent factory for local specialist CLIs (our BaseAgent equivalent)."""

from __future__ import annotations

from typing import Any, Callable, Sequence

from strands import Agent
from strands.models import BedrockModel

from .config import get_aws_region, get_bedrock_model_id
from .tools import V1_TOOLS


def create_research_agent(
    system_prompt: str,
    *,
    tools: Sequence[Callable[..., Any]] | None = None,
    session_manager: Any | None = None,
) -> Agent:
    """
    Build a Strands Agent with pinned Bedrock model and V1 tools by default.

    Does not start AgentCore Runtime / supervisor cloud wiring — local CLI only.
    """
    model = BedrockModel(
        model_id=get_bedrock_model_id(),
        region_name=get_aws_region(),
    )
    kwargs: dict[str, Any] = {
        "model": model,
        "system_prompt": system_prompt,
        "tools": list(tools) if tools is not None else list(V1_TOOLS),
    }
    if session_manager is not None:
        kwargs["session_manager"] = session_manager
    return Agent(**kwargs)


def run_prompt(agent: Agent, prompt: str) -> str:
    """Run one turn and return plain text."""
    result = agent(prompt)
    if result is None:
        return ""
    if isinstance(result, str):
        return result
    message = getattr(result, "message", None)
    if isinstance(message, dict):
        content = message.get("content")
        if isinstance(content, list):
            parts: list[str] = []
            for block in content:
                if isinstance(block, dict) and block.get("text"):
                    parts.append(str(block["text"]))
                elif isinstance(block, str):
                    parts.append(block)
            if parts:
                return "\n".join(parts)
        if message.get("text"):
            return str(message["text"])
    return str(result)
