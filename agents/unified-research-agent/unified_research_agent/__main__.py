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
    create_gateway_mcp_client,
    gateway_enabled,
    list_logical_gateway_tools,
)


def _load_env() -> None:
    """Load .env from the package root if present."""
    package_root = Path(__file__).resolve().parents[1]
    load_dotenv(package_root / ".env", override=False)


def main(argv: list[str] | None = None) -> int:
    _load_env()

    parser = argparse.ArgumentParser(
        description="Unified Research Agent — Bedrock + PubMed (local or Gateway)",
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
    args = parser.parse_args(argv)

    model_id = get_bedrock_model_id()
    region = get_aws_region()
    gw_url = get_agentcore_gateway_url()
    print(f"region={region}", file=sys.stderr)
    print(f"BEDROCK_MODEL_ID={model_id}", file=sys.stderr)
    print(f"USE_GATEWAY_TOOLS={use_gateway_tools()}", file=sys.stderr)
    print(f"AGENTCORE_GATEWAY_URL={gw_url or '(unset)'}", file=sys.stderr)

    if args.list_gateway_tools:
        if not gw_url:
            print("AGENTCORE_GATEWAY_URL is not set", file=sys.stderr)
            return 2
        with create_gateway_mcp_client() as client:
            names = list_logical_gateway_tools(client)
            print("logical_tools=" + ",".join(names))
            return 0 if "pubmed" in names else 1

    if gateway_enabled():
        print("pubmed_path=gateway", file=sys.stderr)
    else:
        print("pubmed_path=local", file=sys.stderr)

    agent = create_agent()
    result = agent(args.prompt)
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
