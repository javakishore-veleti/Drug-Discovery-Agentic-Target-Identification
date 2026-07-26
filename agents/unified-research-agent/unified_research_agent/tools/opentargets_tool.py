"""Strands tool `opentargets` — local adapter or AgentCore Gateway (Story M3.3)."""

from __future__ import annotations

from typing import Any

from strands import tool

from ..gateway_mcp import (
    call_gateway_opentargets,
    create_gateway_mcp_client,
    gateway_enabled,
)
from ..paths import ensure_gateway_database_on_path
from ..tool_trace import forced_error_result

ensure_gateway_database_on_path()
from opentargets.adapter import search_opentargets  # noqa: E402


@tool(
    name="opentargets",
    description=(
        "Search Open Targets Platform for target/disease associations (Ensembl ids). "
        "Use for structured target evidence (e.g. ERBB2 / HER2). "
        "Returns status, ids.ensembl (ENSG… string array), and a short summary. "
        "Optional tool #4 — may be absent from default Gateway deploy."
    ),
)
def opentargets_search(query: str, retmax: int = 8) -> dict[str, Any]:
    """
    Search Open Targets.

    Args:
        query: Target / disease search terms (e.g. ERBB2, HER2, breast cancer).
        retmax: Max hits to return (1–20).
    """
    forced = forced_error_result("opentargets")
    if forced is not None:
        return forced
    if gateway_enabled():
        with create_gateway_mcp_client() as client:
            return call_gateway_opentargets(client, query=query, retmax=retmax)
    return search_opentargets(query, retmax=retmax)
