"""
Local-only agent factories for Stream `agentId` routing.

Production / AWS Stream still uses unified-research-agent only.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable

_REPO = Path(__file__).resolve().parents[1]
_AGENTS = _REPO / "agents"
_URA = _AGENTS / "unified-research-agent"

# Package roots: agents/framework + each specialist folder (contains importable package).
_PATH_ROOTS = [
    _AGENTS,  # `import framework`
    _URA,  # `import unified_research_agent`
    _AGENTS / "drug-profile-analysis-agent",
    _AGENTS / "patient-risk-assessment-agent",
    _AGENTS / "pathway-mapping-agent",
    _AGENTS / "cardioprotection-target-agent",
    _AGENTS / "drug-design-hypothesis-agent",
    _AGENTS / "genetic-risk-assessment",
    _AGENTS / "medical-supervisor-agent",
]

for path in _PATH_ROOTS:
    p = str(path)
    if path.is_dir() and p not in sys.path:
        sys.path.insert(0, p)


def _create_unified() -> Any:
    from unified_research_agent.agent import create_agent

    return create_agent()


def _create_drug_profile() -> Any:
    from drug_profile_analysis_agent.agent import create_agent

    return create_agent()


def _create_patient_risk() -> Any:
    from patient_risk_assessment_agent.agent import create_agent

    return create_agent()


def _create_pathway() -> Any:
    from pathway_mapping_agent.agent import create_agent

    return create_agent()


def _create_cardioprotection() -> Any:
    from cardioprotection_target_agent.agent import create_agent

    return create_agent()


def _create_drug_design() -> Any:
    from drug_design_hypothesis_agent.agent import create_agent

    return create_agent()


def _create_genetic_risk() -> Any:
    from genetic_risk_assessment.agent import create_agent

    return create_agent()


def _create_medical_supervisor() -> Any:
    from medical_supervisor_agent.agent import create_agent

    return create_agent()


# id -> metadata + factory (keep in sync with web/src/chat/localAgents.ts)
AGENT_CATALOG: dict[str, dict[str, Any]] = {
    "unified": {
        "label": "Unified Research Agent (default)",
        "objective": (
            "Single production-style agent covering all five research domains "
            "in one prompt (MoA, population risk, pathways, cardiac safety, design hypotheses)."
        ),
        "output": (
            "Balanced, cited research synthesis with PMID / NCT / ChEMBL "
            "(and Open Targets when used) — general target-ID answers."
        ),
        "factory": _create_unified,
    },
    "drug-profile": {
        "label": "Drug Profile Analysis",
        "objective": (
            "Focus on mechanism of action, molecular targets, toxicity/adverse-effect "
            "signals, and high-level ADME/PK when public evidence exists."
        ),
        "output": (
            "Drug/target profile brief: MoA → safety signals → PK context, "
            "with literature and chemistry citations."
        ),
        "factory": _create_drug_profile,
    },
    "patient-risk": {
        "label": "Patient Risk Assessment",
        "objective": (
            "Focus on population stratification, biomarkers, and vulnerability / AE "
            "patterns from public literature and trials — not individual care plans."
        ),
        "output": (
            "Population-risk research memo with trial/literature IDs "
            "(not clinical recommendations)."
        ),
        "factory": _create_patient_risk,
    },
    "pathway-mapping": {
        "label": "Pathway Mapping",
        "objective": (
            "Focus on protein/pathway relationships, signaling cascades, and network "
            "hypotheses for target identification (literature-first; no dedicated pathway DB in V1)."
        ),
        "output": (
            "Pathway/network framing with honest limits when pathway DBs are unavailable."
        ),
        "factory": _create_pathway,
    },
    "cardioprotection": {
        "label": "Cardioprotection Target",
        "objective": (
            "Focus on cardiac safety / cardiotoxicity signals and protective-mechanism "
            "hypotheses (tumor vs cardiac context when evidence allows)."
        ),
        "output": (
            "Cardio-oncology research note — never monitoring or dosing instructions."
        ),
        "factory": _create_cardioprotection,
    },
    "drug-design": {
        "label": "Drug Design Hypothesis",
        "objective": (
            "Focus on structure/binding and optimization hypotheses grounded in ChEMBL "
            "bioactivity plus literature."
        ),
        "output": (
            "Chemistry/design hypothesis sketch with ChEMBL IDs — no invented PDB/docking."
        ),
        "factory": _create_drug_design,
    },
    "genetic-risk": {
        "label": "Genetic Risk Assessment",
        "objective": (
            "Focus on gene/variant context for a target from public literature; "
            "V1 has no Ensembl/GWAS Gateway tools."
        ),
        "output": (
            "Genetics-oriented research synthesis — not personal genetic counseling."
        ),
        "factory": _create_genetic_risk,
    },
    "medical-supervisor": {
        "label": "Medical Supervisor (local stubs)",
        "objective": (
            "Local experiment router across the five specialist domains "
            "(stubs / in-process) — not a cloud multi-agent Runtime."
        ),
        "output": (
            "Routed or multi-domain synthesis for local exploration; "
            "AWS production stays Unified only."
        ),
        "factory": _create_medical_supervisor,
    },
}

DEFAULT_AGENT_ID = "unified"


def normalize_agent_id(raw: str | None) -> str:
    aid = (raw or "").strip().lower().replace("_", "-")
    if not aid or aid in {"default", "ura", "research"}:
        return DEFAULT_AGENT_ID
    if aid not in AGENT_CATALOG:
        return DEFAULT_AGENT_ID
    return aid


def list_agents() -> list[dict[str, str]]:
    return [
        {
            "id": aid,
            "label": str(meta["label"]),
            "objective": str(meta["objective"]),
            "output": str(meta["output"]),
        }
        for aid, meta in AGENT_CATALOG.items()
    ]


def create_agent_by_id(agent_id: str) -> Any:
    aid = normalize_agent_id(agent_id)
    factory: Callable[[], Any] = AGENT_CATALOG[aid]["factory"]
    return factory()
