"""AgentCore Gateway Lambda target for MCP tool `opentargets` (Story M3.3)."""

from __future__ import annotations

import json
import logging
from typing import Any

from adapter import TOOL_NAME, search_opentargets

logger = logging.getLogger()
logger.setLevel(logging.INFO)

_DELIMITER = "___"


def _tool_name_from_context(context: Any) -> str:
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
    tool_name = _tool_name_from_context(context)
    logger.info(
        "opentargets gateway invoke tool=%s event_keys=%s",
        tool_name,
        list(event or {}),
    )

    if tool_name != TOOL_NAME:
        return {
            "status": "error",
            "tool": TOOL_NAME,
            "message": f"Unknown tool: {tool_name}",
            "ids": {"pmid": [], "nct": [], "chembl": [], "ensembl": []},
            "summary": "",
            "hits": [],
        }

    query = str((event or {}).get("query") or "")
    retmax_raw = (event or {}).get("retmax", 8)
    try:
        retmax = int(retmax_raw)
    except (TypeError, ValueError):
        retmax = 8

    result = search_opentargets(query, retmax=retmax)
    return json.loads(json.dumps(result))
