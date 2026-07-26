"""Strands tool `clinicaltrials` — local adapter or AgentCore Gateway (Story 2.2)."""

from __future__ import annotations

from typing import Any

from strands import tool

from ..gateway_mcp import (
    call_gateway_clinicaltrials,
    create_gateway_mcp_client,
    gateway_enabled,
)
from ..paths import ensure_gateway_database_on_path
from ..tool_trace import forced_error_result

ensure_gateway_database_on_path()
from clinicaltrials.adapter import search_clinicaltrials  # noqa: E402


@tool(
    name="clinicaltrials",
    description=(
        "Search ClinicalTrials.gov for studies. "
        "Use for trial context and NCT IDs related to drugs/targets (e.g. trastuzumab/HER2). "
        "Returns status, ids.nct (NCT######## string array), and a short summary."
    ),
)
def clinicaltrials_search(query: str, retmax: int = 8) -> dict[str, Any]:
    """
    Search ClinicalTrials.gov.

    Args:
        query: Search terms (e.g. trastuzumab HER2 breast cancer).
        retmax: Max NCT IDs to return (1–20).
    """
    forced = forced_error_result("clinicaltrials")
    if forced is not None:
        return forced
    if gateway_enabled():
        with create_gateway_mcp_client() as client:
            return call_gateway_clinicaltrials(client, query=query, retmax=retmax)
    return search_clinicaltrials(query, retmax=retmax)
