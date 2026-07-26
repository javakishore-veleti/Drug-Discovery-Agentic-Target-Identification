"""Runtime configuration for the Unified Research Agent (AD-6)."""

from __future__ import annotations

import os

# Active US inference profile (Bedrock us-east-1, 2026-07).
# Spine AD-6 originally pinned us.anthropic.claude-sonnet-4-20250514-v1:0;
# that id is now Legacy/EOL in many accounts — use Sonnet 4.6 instead.
DEFAULT_BEDROCK_MODEL_ID = "us.anthropic.claude-sonnet-4-6"

# Fallback if 4.6 is unavailable
FALLBACK_BEDROCK_MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

DEFAULT_AWS_REGION = "us-east-1"


def get_bedrock_model_id() -> str:
    """Return Bedrock model id from BEDROCK_MODEL_ID or the AD-6 default pin."""
    return os.environ.get("BEDROCK_MODEL_ID", DEFAULT_BEDROCK_MODEL_ID).strip()


def get_aws_region() -> str:
    """Return AWS region (defaults to us-east-1)."""
    return (
        os.environ.get("AWS_REGION")
        or os.environ.get("AWS_DEFAULT_REGION")
        or DEFAULT_AWS_REGION
    ).strip()
