"""Minimal local CLI helper for specialist agent packages."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from .base_agent import create_research_agent, run_prompt
from .config import get_aws_region, get_bedrock_model_id


def load_agent_env(package_root: Path) -> None:
    """Load .env from the agent package and optional unified-research-agent/.env."""
    load_dotenv(package_root / ".env", override=False)
    ura_env = package_root.parent / "unified-research-agent" / ".env"
    load_dotenv(ura_env, override=False)


def main_for_agent(
    *,
    agent_title: str,
    system_prompt: str,
    package_root: Path,
    argv: list[str] | None = None,
) -> int:
    load_agent_env(package_root)
    parser = argparse.ArgumentParser(description=f"{agent_title} (local CLI)")
    parser.add_argument("prompt", nargs="+", help="Research question")
    args = parser.parse_args(argv)
    prompt = " ".join(args.prompt).strip()
    if not prompt:
        print("Provide a non-empty prompt", file=sys.stderr)
        return 2

    print(f"agent={agent_title}", file=sys.stderr)
    print(f"model={get_bedrock_model_id()} region={get_aws_region()}", file=sys.stderr)
    print("mode=local_cli (not AgentCore Runtime)", file=sys.stderr)

    agent = create_research_agent(system_prompt)
    print(run_prompt(agent, prompt))
    return 0
