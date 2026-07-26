"""CLI entrypoint: python -m unified_research_agent \"your prompt\"."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from .agent import create_agent
from .config import get_aws_region, get_bedrock_model_id


def _load_env() -> None:
    """Load .env from the package root if present."""
    package_root = Path(__file__).resolve().parents[1]
    load_dotenv(package_root / ".env", override=False)


def main(argv: list[str] | None = None) -> int:
    _load_env()

    parser = argparse.ArgumentParser(
        description="Unified Research Agent — local Bedrock + PubMed CLI (Epic 1)",
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        default="Reply with exactly one word: ok",
        help="Prompt to send to the agent (default: trivial smoke prompt)",
    )
    args = parser.parse_args(argv)

    model_id = get_bedrock_model_id()
    region = get_aws_region()
    print(f"region={region}", file=sys.stderr)
    print(f"BEDROCK_MODEL_ID={model_id}", file=sys.stderr)

    agent = create_agent()
    result = agent(args.prompt)
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
