"""Strands tool wrapping the shared PubMed adapter (Story 1.3)."""

from __future__ import annotations

from typing import Any

from strands import tool

from ..paths import ensure_gateway_database_on_path

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
    return search_pubmed(query, retmax=retmax)
