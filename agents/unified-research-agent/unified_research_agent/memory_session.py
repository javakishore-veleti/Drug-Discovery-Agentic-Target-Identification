"""AgentCore Memory session wiring for in-session multi-turn (Story 3.2 / AD-7)."""

from __future__ import annotations

from typing import Any

from .config import (
    get_agentcore_actor_id,
    get_agentcore_memory_id,
    get_aws_region,
)


def memory_enabled() -> bool:
    """True when AGENTCORE_MEMORY_ID is set (STM path active)."""
    return bool(get_agentcore_memory_id())


def build_memory_session_manager(session_id: str) -> Any:
    """
    Build AgentCoreMemorySessionManager for one Chat Session key.

    Callers should use as a context manager so buffered events flush on exit.
    """
    memory_id = get_agentcore_memory_id()
    if not memory_id:
        raise RuntimeError("AGENTCORE_MEMORY_ID is required for Memory sessions")
    sid = (session_id or "").strip()
    if not sid:
        raise RuntimeError("session_id is required when AGENTCORE_MEMORY_ID is set")

    from bedrock_agentcore.memory.integrations.strands.config import (
        AgentCoreMemoryConfig,
    )
    from bedrock_agentcore.memory.integrations.strands.session_manager import (
        AgentCoreMemorySessionManager,
    )

    config = AgentCoreMemoryConfig(
        memory_id=memory_id,
        session_id=sid,
        actor_id=get_agentcore_actor_id(),
        batch_size=1,
    )
    return AgentCoreMemorySessionManager(
        agentcore_memory_config=config,
        region_name=get_aws_region(),
    )
