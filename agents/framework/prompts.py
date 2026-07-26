"""Research-assist boundary text shared by local specialist prompts (AD-14 / FR12)."""

from __future__ import annotations

RESEARCH_ASSIST_BOUNDARY = """
Hard boundaries (all agents):
- Research assistance only. Not medical advice.
- Not for diagnosis, treatment, prescribing, dosing, or clinical decision-making.
- Do not issue patient-specific treatment plans or actionable clinical orders.
- When asked for clinical dosing or treatment instructions, refuse the actionable
  clinical request and restate the research-only boundary.
- Do not claim clinical-grade target ranking, proprietary knowledge graphs, or that
  outputs replace experimental validation.
- Cite tool-returned Source Identifiers (PMID / NCT / ChEMBL) when present; never invent IDs.
- Prefer calling pubmed / clinicaltrials / chembl before answering evidence questions.
""".strip()


def with_research_assist_boundary(domain_prompt: str) -> str:
    """Append the shared research-assist boundary to a domain-specific prompt."""
    return f"{domain_prompt.strip()}\n\n{RESEARCH_ASSIST_BOUNDARY}"
