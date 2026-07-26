"""
Shared V1 tool result helpers (Story 2.4 / AD-8 / AD-9).

Logical MCP tool names and the error/ok envelope used by Gateway adapters.
"""

from __future__ import annotations

from typing import Any

# AD-3 / FR-16 — default Gateway exposes exactly these logical names.
V1_LOGICAL_TOOLS: frozenset[str] = frozenset({"pubmed", "clinicaltrials", "chembl"})


def empty_ids() -> dict[str, list[str]]:
    return {"pmid": [], "nct": [], "chembl": []}


def error_result(tool: str, message: str) -> dict[str, Any]:
    """Safe tool_result error envelope (no secrets / stack traces)."""
    return {
        "status": "error",
        "tool": tool,
        "message": message,
        "ids": empty_ids(),
        "summary": "",
    }


def assert_exact_v1_tools(logical_names: set[str] | list[str] | frozenset[str]) -> None:
    """Raise ValueError unless the set is exactly the three V1 tools."""
    got = frozenset(logical_names)
    if got != V1_LOGICAL_TOOLS:
        raise ValueError(
            f"Expected exactly {sorted(V1_LOGICAL_TOOLS)}, got {sorted(got)}"
        )
