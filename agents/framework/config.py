"""Shared env config (aligned with unified-research-agent / AD-6)."""

from __future__ import annotations

import os

DEFAULT_BEDROCK_MODEL_ID = "us.anthropic.claude-sonnet-4-6"
DEFAULT_AWS_REGION = "us-east-1"


def get_bedrock_model_id() -> str:
    return os.environ.get("BEDROCK_MODEL_ID", DEFAULT_BEDROCK_MODEL_ID).strip()


def get_aws_region() -> str:
    return (
        os.environ.get("AWS_REGION")
        or os.environ.get("AWS_DEFAULT_REGION")
        or DEFAULT_AWS_REGION
    ).strip()


def get_agentcore_gateway_url() -> str:
    return os.environ.get("AGENTCORE_GATEWAY_URL", "").strip()
