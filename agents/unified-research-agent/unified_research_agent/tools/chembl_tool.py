"""Strands tool `chembl` — local adapter or AgentCore Gateway (Story 2.3)."""

from __future__ import annotations

from typing import Any

from strands import tool

from ..gateway_mcp import call_gateway_chembl, create_gateway_mcp_client, gateway_enabled
from ..paths import ensure_gateway_database_on_path
from ..tool_trace import forced_error_result

ensure_gateway_database_on_path()
from chembl.adapter import search_chembl  # noqa: E402


@tool(
    name="chembl",
    description=(
        "Search ChEMBL for molecules / bioactives. "
        "Use for chemistry and drug-identity questions (e.g. trastuzumab, HER2 ADCs). "
        "Returns status, ids.chembl (CHEMBL##### string array), and a short summary."
    ),
)
def chembl_search(query: str, retmax: int = 8) -> dict[str, Any]:
    """
    Search ChEMBL.

    Args:
        query: Molecule / drug search terms (e.g. trastuzumab).
        retmax: Max ChEMBL IDs to return (1–20).
    """
    forced = forced_error_result("chembl")
    if forced is not None:
        return forced
    if gateway_enabled():
        with create_gateway_mcp_client() as client:
            return call_gateway_chembl(client, query=query, retmax=retmax)
    return search_chembl(query, retmax=retmax)
