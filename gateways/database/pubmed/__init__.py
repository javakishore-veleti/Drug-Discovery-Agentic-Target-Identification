"""PubMed tool adapter (shared by local agent and future Gateway Lambda)."""

from .adapter import TOOL_NAME, search_pubmed

__all__ = ["TOOL_NAME", "search_pubmed"]
