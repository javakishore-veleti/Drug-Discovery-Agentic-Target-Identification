"""Strands tool `pubmed` — local adapter or AgentCore Gateway (Story 2.1)."""

from __future__ import annotations

from typing import Any

from strands import tool

from ..gateway_mcp import call_gateway_pubmed, create_gateway_mcp_client, gateway_enabled
from ..paths import ensure_gateway_database_on_path
from ..tool_trace import forced_error_result

ensure_gateway_database_on_path()
from pubmed.adapter import search_pubmed  # noqa: E402  — path bootstrap above


@tool(
    name="pubmed",
    description=(
        "Search PubMed via NCBI E-utilities for biomedical literature. "
        "Use for mechanism, safety, and target-identification questions. "
        "Returns status, ids.pmid (string array), and a short summary of hits."
    ),
)
def pubmed_search(query: str, retmax: int = 8) -> dict[str, Any]:
    """
    Search PubMed.

    Args:
        query: PubMed/Entrez search terms (e.g. trastuzumab mechanism of action).
        retmax: Max PMIDs to return (1–20).
    """
    forced = forced_error_result("pubmed")
    if forced is not None:
        return forced
    if gateway_enabled():
        with create_gateway_mcp_client() as client:
            return call_gateway_pubmed(client, query=query, retmax=retmax)
    return search_pubmed(query, retmax=retmax)
