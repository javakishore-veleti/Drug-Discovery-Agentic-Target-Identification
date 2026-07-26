"""CLI entrypoint: python -m unified_research_agent \"your prompt\"."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from .agent import create_agent
from .config import (
    get_agentcore_gateway_url,
    get_aws_region,
    get_bedrock_model_id,
    use_gateway_tools,
)
from .gateway_mcp import (
    V1_LOGICAL_TOOLS,
    assert_exact_v1_gateway_tools,
    call_gateway_chembl,
    call_gateway_clinicaltrials,
    call_gateway_pubmed,
    create_gateway_mcp_client,
    gateway_enabled,
    is_safe_error_result,
    list_logical_gateway_tools,
)


def _load_env() -> None:
    """Load .env from the package root if present."""
    package_root = Path(__file__).resolve().parents[1]
    load_dotenv(package_root / ".env", override=False)


def _smoke_epic2() -> int:
    """
    Story 2.4 smoke:
    - Gateway lists exactly the three V1 tools
    - Forced empty-query failure → status:error + tool + message
    - Agent accepts another turn after a failed tool call (same process)
    """
    gw_url = get_agentcore_gateway_url()
    if not gw_url:
        print("AGENTCORE_GATEWAY_URL is not set", file=sys.stderr)
        return 2

    with create_gateway_mcp_client() as client:
        names = list_logical_gateway_tools(client)
        print("logical_tools=" + ",".join(names))
        try:
            assert_exact_v1_gateway_tools(names)
        except ValueError as exc:
            print(f"v1_tools_mismatch: {exc}", file=sys.stderr)
            return 1
        print("v1_tools_exact=ok", file=sys.stderr)

        callers = {
            "pubmed": call_gateway_pubmed,
            "clinicaltrials": call_gateway_clinicaltrials,
            "chembl": call_gateway_chembl,
        }
        for tool_name in sorted(V1_LOGICAL_TOOLS):
            result = callers[tool_name](client, query="", retmax=1)
            print(
                f"forced_error[{tool_name}]="
                f"status={result.get('status')} tool={result.get('tool')} "
                f"message={result.get('message')!r}",
                file=sys.stderr,
            )
            if not is_safe_error_result(result, expected_tool=tool_name):
                print(f"bad_error_shape for {tool_name}: {result}", file=sys.stderr)
                return 1
        print("forced_errors=ok", file=sys.stderr)

    # Same process: after tool failures, agent still accepts a new turn (AD-8).
    agent = create_agent()
    follow_up = agent("Reply with exactly one word: ok")
    text = str(follow_up).strip()
    print(f"post_failure_turn={text!r}", file=sys.stderr)
    if "ok" not in text.lower():
        print("post_failure_turn did not include ok", file=sys.stderr)
        return 1
    print("epic2_smoke=ok", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    _load_env()

    parser = argparse.ArgumentParser(
        description="Unified Research Agent — Bedrock + Gateway evidence tools",
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        default="Reply with exactly one word: ok",
        help="Prompt to send to the agent (default: trivial smoke prompt)",
    )
    parser.add_argument(
        "--list-gateway-tools",
        action="store_true",
        help="List logical MCP tools from AgentCore Gateway and exit",
    )
    parser.add_argument(
        "--smoke-epic2",
        action="store_true",
        help="Story 2.4: exact V1 tools + forced error shape + post-failure turn",
    )
    args = parser.parse_args(argv)

    model_id = get_bedrock_model_id()
    region = get_aws_region()
    gw_url = get_agentcore_gateway_url()
    print(f"region={region}", file=sys.stderr)
    print(f"BEDROCK_MODEL_ID={model_id}", file=sys.stderr)
    print(f"USE_GATEWAY_TOOLS={use_gateway_tools()}", file=sys.stderr)
    print(f"AGENTCORE_GATEWAY_URL={gw_url or '(unset)'}", file=sys.stderr)

    if args.smoke_epic2:
        return _smoke_epic2()

    if args.list_gateway_tools:
        if not gw_url:
            print("AGENTCORE_GATEWAY_URL is not set", file=sys.stderr)
            return 2
        with create_gateway_mcp_client() as client:
            names = list_logical_gateway_tools(client)
            print("logical_tools=" + ",".join(names))
            try:
                assert_exact_v1_gateway_tools(names)
            except ValueError as exc:
                print(f"v1_tools_mismatch: {exc}", file=sys.stderr)
                return 1
            return 0

    if gateway_enabled():
        print("tools_path=gateway", file=sys.stderr)
    else:
        print("tools_path=local", file=sys.stderr)

    agent = create_agent()
    result = agent(args.prompt)
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
