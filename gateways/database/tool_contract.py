"""
Shared V1 tool result helpers (Story 2.4 / AD-8 / AD-9).

Logical MCP tool names and the error/ok envelope used by Gateway adapters.
"""

from __future__ import annotations

from typing import Any

# AD-3 / FR-16 — default Gateway exposes exactly these logical names.
V1_LOGICAL_TOOLS: frozenset[str] = frozenset({"pubmed", "clinicaltrials", "chembl"})
# Story M3.3 — optional fourth tool when CDK context enableTool4=true
TOOL4_OPENTARGETS = "opentargets"
V1_PLUS_TOOL4: frozenset[str] = V1_LOGICAL_TOOLS | {TOOL4_OPENTARGETS}


def empty_ids() -> dict[str, list[str]]:
    return {"pmid": [], "nct": [], "chembl": [], "ensembl": []}


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


def assert_gateway_tools(logical_names: set[str] | list[str] | frozenset[str]) -> None:
    """Allow exactly V1 three tools, or V1 + opentargets (M3.3)."""
    got = frozenset(logical_names)
    if got not in (V1_LOGICAL_TOOLS, V1_PLUS_TOOL4):
        raise ValueError(
            f"Expected {sorted(V1_LOGICAL_TOOLS)} or {sorted(V1_PLUS_TOOL4)}, "
            f"got {sorted(got)}"
        )
