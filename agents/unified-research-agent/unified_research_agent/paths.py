"""Ensure shared gateway adapters under gateways/database are importable."""

from __future__ import annotations

import sys
from pathlib import Path


def ensure_gateway_database_on_path() -> Path:
    """
    Insert ``<repo>/gateways/database`` on sys.path so ``import pubmed`` works.

    Layout: agents/unified-research-agent/unified_research_agent/paths.py
    → parents[3] = repository root.
    """
    repo_root = Path(__file__).resolve().parents[3]
    gateway_db = repo_root / "gateways" / "database"
    path_str = str(gateway_db)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)
    return gateway_db
