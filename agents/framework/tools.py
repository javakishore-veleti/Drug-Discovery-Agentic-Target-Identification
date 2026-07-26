"""
Wire V1 tools from the production unified-research-agent package.

Local specialists reuse ``pubmed`` / ``clinicaltrials`` / ``chembl`` (local adapters
or Gateway MCP when ``AGENTCORE_GATEWAY_URL`` is set) — no proprietary tool copies.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable


def _ensure_unified_on_path() -> None:
    agents_root = Path(__file__).resolve().parents[1]
    ura_root = agents_root / "unified-research-agent"
    if ura_root.is_dir() and str(ura_root) not in sys.path:
        sys.path.insert(0, str(ura_root))


_ensure_unified_on_path()

from unified_research_agent.tools import (  # noqa: E402
    chembl_search,
    clinicaltrials_search,
    pubmed_search,
)

V1_TOOLS: list[Callable[..., Any]] = [
    pubmed_search,
    clinicaltrials_search,
    chembl_search,
]

__all__ = [
    "V1_TOOLS",
    "chembl_search",
    "clinicaltrials_search",
    "pubmed_search",
]
