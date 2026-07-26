"""
Shared local agent helpers for Agentic Target ID.

Specialist / supervisor / genetic packages use this for config, research-assist
prompt boundaries, tool wiring, and Strands agent construction. Production cloud
path remains ``agents/unified-research-agent`` only.
"""

from .base_agent import create_research_agent, run_prompt
from .config import get_aws_region, get_bedrock_model_id
from .prompts import RESEARCH_ASSIST_BOUNDARY, with_research_assist_boundary

__all__ = [
    "RESEARCH_ASSIST_BOUNDARY",
    "create_research_agent",
    "get_aws_region",
    "get_bedrock_model_id",
    "run_prompt",
    "with_research_assist_boundary",
]
