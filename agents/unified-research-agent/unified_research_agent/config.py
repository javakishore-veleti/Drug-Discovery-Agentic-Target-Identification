"""Runtime configuration for the Unified Research Agent (AD-6)."""

from __future__ import annotations

import os

# Architecture spine AD-6 pin
DEFAULT_BEDROCK_MODEL_ID = "us.anthropic.claude-sonnet-4-20250514-v1:0"

# Documented fallback when the pinned Sonnet 4 profile is unavailable
FALLBACK_BEDROCK_MODEL_ID = "anthropic.claude-3-7-sonnet-20250219-v1:0"

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
