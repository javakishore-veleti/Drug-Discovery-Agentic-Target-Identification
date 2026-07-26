"""ChEMBL tool adapter (shared by Gateway Lambda and local agent)."""

from .adapter import TOOL_NAME, search_chembl

__all__ = ["TOOL_NAME", "search_chembl"]
