"""ClinicalTrials.gov tool adapter (shared by Gateway Lambda and local agent)."""

from .adapter import TOOL_NAME, search_clinicaltrials

__all__ = ["TOOL_NAME", "search_clinicaltrials"]
