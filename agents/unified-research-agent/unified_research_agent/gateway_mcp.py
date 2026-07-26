"""
AgentCore Gateway MCP client (Stories 2.1–2.4).

Uses SigV4 via mcp-proxy-for-aws against an IAM-authorized Gateway.
Normalizes wire names like `pubmed___pubmed` → logical `pubmed` (AD-3).
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

from strands.tools.mcp import MCPClient

from .config import get_agentcore_gateway_url, get_aws_region, use_gateway_tools

logger = logging.getLogger(__name__)

LOGICAL_PUBMED = "pubmed"
LOGICAL_CLINICALTRIALS = "clinicaltrials"
LOGICAL_CHEMBL = "chembl"
LOGICAL_OPENTARGETS = "opentargets"
_DELIMITER = "___"

# Keep in sync with gateways/database/tool_contract.py + CDK V1_LOGICAL_TOOLS
V1_LOGICAL_TOOLS: frozenset[str] = frozenset(
    {LOGICAL_PUBMED, LOGICAL_CLINICALTRIALS, LOGICAL_CHEMBL}
)
# Default V1 (FR-16) plus optional tool #4 when Gateway deployed with enableTool4
V1_PLUS_TOOL4: frozenset[str] = V1_LOGICAL_TOOLS | {LOGICAL_OPENTARGETS}


def _ensure_tool_contract_on_path() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    gateway_db = repo_root / "gateways" / "database"
    path_str = str(gateway_db)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)


def assert_exact_v1_gateway_tools(logical_names: list[str] | set[str]) -> None:
    """
    Story 2.4 / M3.3 — Gateway exposes exactly V1 three tools, or V1+opentargets
    when tool #4 is enabled on the Gateway deploy.
    """
    _ensure_tool_contract_on_path()
    from tool_contract import assert_gateway_tools  # noqa: E402

    assert_gateway_tools(logical_names)


def logical_tool_name(wire_name: str) -> str:
    """Map Gateway `${target}___${tool}` wire names to logical AD-3 names."""
    name = (wire_name or "").strip()
    if _DELIMITER in name:
        return name.rsplit(_DELIMITER, 1)[-1]
    return name


def wire_tool_name_for_logical(tools: list[Any], logical: str) -> str | None:
    """Find the Gateway wire name for a logical tool (prefer exact, then suffix)."""
    exact = [t for t in tools if getattr(t, "tool_name", None) == logical]
    if exact:
        return exact[0].tool_name
    suffixed = [
        t
        for t in tools
        if logical_tool_name(getattr(t, "tool_name", "") or "") == logical
    ]
    if suffixed:
        return suffixed[0].tool_name
    return None


def create_gateway_mcp_client() -> MCPClient:
    """Build an MCPClient factory wired for AgentCore Gateway + IAM SigV4."""
    from mcp_proxy_for_aws.client import aws_iam_streamablehttp_client

    url = get_agentcore_gateway_url()
    if not url:
        raise RuntimeError("AGENTCORE_GATEWAY_URL is required for Gateway tools")

    region = get_aws_region()

    def _transport():
        return aws_iam_streamablehttp_client(
            endpoint=url,
            aws_region=region,
            aws_service="bedrock-agentcore",
        )

    return MCPClient(_transport)


def list_logical_gateway_tools(client: MCPClient) -> list[str]:
    """List logical tool names visible through the Gateway."""
    tools = client.list_tools_sync()
    return sorted({logical_tool_name(t.tool_name) for t in tools})


def is_safe_error_result(result: dict[str, Any], *, expected_tool: str) -> bool:
    """True if result matches AD-8 error tool_result (status/tool/message/ids)."""
    if result.get("status") != "error":
        return False
    if result.get("tool") != expected_tool:
        return False
    message = result.get("message")
    if not isinstance(message, str) or not message.strip():
        return False
    # No stack-trace-ish leakage in user-visible message
    lowered = message.lower()
    if "traceback" in lowered or "secret" in lowered:
        return False
    ids = result.get("ids")
    if not isinstance(ids, dict):
        return False
    for key in ("pmid", "nct", "chembl"):
        if key not in ids or not isinstance(ids[key], list):
            return False
    return True


def call_gateway_tool(
    client: MCPClient,
    *,
    logical_name: str,
    arguments: dict[str, Any],
    tool_use_id: str,
) -> dict[str, Any]:
    """Call a Gateway MCP tool by logical AD-3 name; return adapter-shaped dict."""
    tools = client.list_tools_sync()
    wire = wire_tool_name_for_logical(tools, logical_name)
    if not wire:
        names = [getattr(t, "tool_name", "?") for t in tools]
        raise RuntimeError(
            f"Gateway did not expose {logical_name} (logical). Wire tools seen: {names}"
        )

    result = client.call_tool_sync(
        tool_use_id=tool_use_id,
        name=wire,
        arguments=arguments,
    )
    return _parse_tool_result(result, tool=logical_name)


def call_gateway_pubmed(
    client: MCPClient,
    *,
    query: str,
    retmax: int = 8,
) -> dict[str, Any]:
    """Call Gateway MCP tool pubmed and return a parsed adapter-shaped dict."""
    return call_gateway_tool(
        client,
        logical_name=LOGICAL_PUBMED,
        arguments={"query": query, "retmax": retmax},
        tool_use_id="gateway-pubmed-1",
    )


def call_gateway_clinicaltrials(
    client: MCPClient,
    *,
    query: str,
    retmax: int = 8,
) -> dict[str, Any]:
    """Call Gateway MCP tool clinicaltrials and return a parsed adapter-shaped dict."""
    return call_gateway_tool(
        client,
        logical_name=LOGICAL_CLINICALTRIALS,
        arguments={"query": query, "retmax": retmax},
        tool_use_id="gateway-clinicaltrials-1",
    )


def call_gateway_chembl(
    client: MCPClient,
    *,
    query: str,
    retmax: int = 8,
) -> dict[str, Any]:
    """Call Gateway MCP tool chembl and return a parsed adapter-shaped dict."""
    return call_gateway_tool(
        client,
        logical_name=LOGICAL_CHEMBL,
        arguments={"query": query, "retmax": retmax},
        tool_use_id="gateway-chembl-1",
    )


def call_gateway_opentargets(
    client: MCPClient,
    *,
    query: str,
    retmax: int = 8,
) -> dict[str, Any]:
    """Call Gateway MCP tool opentargets (Story M3.3) when deployed."""
    return call_gateway_tool(
        client,
        logical_name=LOGICAL_OPENTARGETS,
        arguments={"query": query, "retmax": retmax},
        tool_use_id="gateway-opentargets-1",
    )


def _parse_tool_result(result: Any, *, tool: str = LOGICAL_PUBMED) -> dict[str, Any]:
    """Best-effort unwrap of MCP / Strands tool result into adapter dict."""
    if isinstance(result, dict) and "ids" in result:
        return result

    structured = None
    if isinstance(result, dict):
        structured = result.get("structuredContent")
    else:
        structured = getattr(result, "structuredContent", None)
    if isinstance(structured, dict) and "ids" in structured:
        return structured
    if isinstance(structured, dict) and "result" in structured:
        inner = structured["result"]
        if isinstance(inner, dict):
            return inner
        if isinstance(inner, str):
            try:
                parsed = json.loads(inner)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass

    content = getattr(result, "content", None)
    if content is None and isinstance(result, dict):
        content = result.get("content")

    texts: list[str] = []
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict):
                if block.get("text") is not None:
                    texts.append(str(block.get("text") or ""))
                elif "json" in block:
                    texts.append(json.dumps(block["json"]))
            else:
                text = getattr(block, "text", None)
                if text is not None:
                    texts.append(str(text))
    elif isinstance(result, str):
        texts.append(result)

    for text in texts:
        text = text.strip()
        if not text:
            continue
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            continue

    if isinstance(result, dict):
        return result

    return {
        "status": "error",
        "tool": tool,
        "message": f"Unrecognized Gateway tool result: {type(result).__name__}",
        "ids": {"pmid": [], "nct": [], "chembl": []},
        "summary": "",
    }


def gateway_enabled() -> bool:
    """True when the agent should prefer Gateway over the local PubMed path."""
    return use_gateway_tools() and bool(get_agentcore_gateway_url())
