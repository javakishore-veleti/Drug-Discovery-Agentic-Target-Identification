"""In-process specialist stubs (local only — not AgentCore multi-agent)."""

from __future__ import annotations

import sys
from pathlib import Path

from strands import tool

_AGENTS = Path(__file__).resolve().parents[2]
if str(_AGENTS) not in sys.path:
    sys.path.insert(0, str(_AGENTS))

for _name in (
    "drug-profile-analysis-agent",
    "patient-risk-assessment-agent",
    "pathway-mapping-agent",
    "cardioprotection-target-agent",
    "drug-design-hypothesis-agent",
):
    _p = _AGENTS / _name
    if _p.is_dir() and str(_p) not in sys.path:
        sys.path.insert(0, str(_p))


def _run_specialist(module_path: str, create_name: str, question: str) -> str:
    import importlib

    from framework.base_agent import run_prompt

    mod = importlib.import_module(module_path)
    create = getattr(mod, create_name)
    agent = create()
    return run_prompt(agent, question)


@tool(
    name="route_drug_profile",
    description="Local stub: drug profile / MoA / toxicity research specialist.",
)
def route_drug_profile(question: str) -> str:
    return _run_specialist(
        "drug_profile_analysis_agent.agent", "create_agent", question
    )


@tool(
    name="route_patient_risk",
    description="Local stub: population / patient-risk research specialist.",
)
def route_patient_risk(question: str) -> str:
    return _run_specialist(
        "patient_risk_assessment_agent.agent", "create_agent", question
    )


@tool(
    name="route_pathway",
    description="Local stub: pathway / network research specialist.",
)
def route_pathway(question: str) -> str:
    return _run_specialist("pathway_mapping_agent.agent", "create_agent", question)


@tool(
    name="route_cardioprotection",
    description="Local stub: cardiac safety / cardioprotection research specialist.",
)
def route_cardioprotection(question: str) -> str:
    return _run_specialist(
        "cardioprotection_target_agent.agent", "create_agent", question
    )


@tool(
    name="route_drug_design",
    description="Local stub: drug design hypothesis research specialist.",
)
def route_drug_design(question: str) -> str:
    return _run_specialist(
        "drug_design_hypothesis_agent.agent", "create_agent", question
    )


SPECIALIST_STUB_TOOLS = [
    route_drug_profile,
    route_patient_risk,
    route_pathway,
    route_cardioprotection,
    route_drug_design,
]
