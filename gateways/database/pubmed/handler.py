"""
AgentCore Gateway Lambda target for MCP tool `pubmed`.

Reuses shared adapter.search_pubmed (Story 1.3 / AD-9 / AD-15).
Event = tool args; tool name is in Lambda client context (may be target___pubmed).
"""

from __future__ import annotations

import json
import logging
from typing import Any

from adapter import TOOL_NAME, search_pubmed

logger = logging.getLogger()
logger.setLevel(logging.INFO)

_DELIMITER = "___"


def _tool_name_from_context(context: Any) -> str:
    """Extract logical tool name, stripping AgentCore `${target}___` prefix."""
    custom = getattr(getattr(context, "client_context", None), "custom", None) or {}
    raw = (
        custom.get("bedrockAgentCoreToolName")
        or custom.get("bedrockagentcoreToolName")
        or TOOL_NAME
    )
    name = str(raw)
    if _DELIMITER in name:
        return name.split(_DELIMITER, 1)[1]
    return name


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Gateway Lambda entrypoint.

    Returns the shared adapter result dict (includes ids.pmid).
    """
    tool_name = _tool_name_from_context(context)
    logger.info("pubmed gateway invoke tool=%s event_keys=%s", tool_name, list(event or {}))

    if tool_name != TOOL_NAME:
        return {
            "status": "error",
            "tool": TOOL_NAME,
            "message": f"Unknown tool: {tool_name}",
            "ids": {"pmid": [], "nct": [], "chembl": []},
            "summary": "",
            "articles": [],
        }

    query = str((event or {}).get("query") or "")
    retmax_raw = (event or {}).get("retmax", 8)
    try:
        retmax = int(retmax_raw)
    except (TypeError, ValueError):
        retmax = 8

    result = search_pubmed(query, retmax=retmax)
    # Ensure JSON-serializable (Gateway MCP transport)
    return json.loads(json.dumps(result))
