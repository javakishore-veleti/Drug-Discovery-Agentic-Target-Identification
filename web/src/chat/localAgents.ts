/** Local Stream agent picker — ids must match local/agent_registry.py. */

export type LocalAgentOption = {
  id: string;
  label: string;
  /** One-line unique focus */
  objective: string;
  /** What kind of answer this agent tries to produce */
  output: string;
  /** How this lens helps early target identification */
  targetIdHelp: string;
};

export const DEFAULT_LOCAL_AGENT_ID = "unified";

export const LOCAL_AGENTS: readonly LocalAgentOption[] = [
  {
    id: "unified",
    label: "Unified Research Agent (default)",
    objective:
      "Single production-style agent covering all five research domains in one prompt (MoA, population risk, pathways, cardiac safety, design hypotheses).",
    output:
      "Balanced, cited research synthesis with PMID / NCT / ChEMBL (and Open Targets when used) — general target-ID answers, not a narrow specialty lens.",
    targetIdHelp:
      "End-to-end Target ID starting point: one agent can connect disease biology → target rationale → safety/chemistry evidence without switching specialists.",
  },
  {
    id: "drug-profile",
    label: "Drug Profile Analysis",
    objective:
      "Focus on mechanism of action, molecular targets, toxicity/adverse-effect signals, and high-level ADME/PK when public evidence exists.",
    output:
      "Drug/target profile brief: MoA → safety signals → PK context, with literature and chemistry citations.",
    targetIdHelp:
      "Helps ask “is this the right molecule/target?” — clarifies what the target does, how a drug modulates it, and early safety/PK red flags before deeper validation.",
  },
  {
    id: "patient-risk",
    label: "Patient Risk Assessment",
    objective:
      "Focus on population stratification, biomarkers, and vulnerability / AE patterns from public literature and trials — not individual care plans.",
    output:
      "Population-risk research memo: who appears more vulnerable in published evidence, with trial/literature IDs (not clinical recommendations).",
    targetIdHelp:
      "Helps ask “which patients / contexts matter?” — biomarker and population signals that shape whether a target is worth pursuing for a defined indication.",
  },
  {
    id: "pathway-mapping",
    label: "Pathway Mapping",
    objective:
      "Focus on protein/pathway relationships, signaling cascades, and network hypotheses for target identification (literature-first; no dedicated pathway DB in V1).",
    output:
      "Pathway/network framing: how a target/drug sits in signaling context, with honest limits when pathway DBs are unavailable.",
    targetIdHelp:
      "Helps ask “where does this sit in disease biology?” — maps the target into pathways/networks so you can judge causality, redundancy, and related nodes.",
  },
  {
    id: "cardioprotection",
    label: "Cardioprotection Target",
    objective:
      "Focus on cardiac safety / cardiotoxicity signals and protective-mechanism hypotheses (tumor vs cardiac context when evidence allows).",
    output:
      "Cardio-oncology research note: cardiotoxicity mechanisms, risk signals, protective hypotheses — never monitoring or dosing instructions.",
    targetIdHelp:
      "Helps ask “will this target/therapy carry cardiac risk?” — surfaces cardiotoxicity vs cardioprotection evidence that can kill or reshape a Target ID bet early.",
  },
  {
    id: "drug-design",
    label: "Drug Design Hypothesis",
    objective:
      "Focus on structure/binding and optimization hypotheses grounded in ChEMBL bioactivity plus literature (selectivity, off-target, safer targeting).",
    output:
      "Chemistry/design hypothesis sketch with ChEMBL IDs and literature support — no invented PDB/docking results.",
    targetIdHelp:
      "Helps ask “is it druggable / how might we modulate it?” — chemistry and bioactivity context that bridges Target ID toward hit/lead thinking.",
  },
  {
    id: "genetic-risk",
    label: "Genetic Risk Assessment",
    objective:
      "Focus on gene/variant context for a target from public literature (e.g. ERBB2/HER2); V1 has no Ensembl/GWAS Gateway tools.",
    output:
      "Genetics-oriented research synthesis for scientists — not personal genetic counseling or individual clinical risk scores.",
    targetIdHelp:
      "Helps ask “is genetics on our side?” — gene/variant evidence that supports (or weakens) the target–disease link from public literature.",
  },
  {
    id: "medical-supervisor",
    label: "Medical Supervisor (local stubs)",
    objective:
      "Local experiment router: coordinate conceptually across the five specialist domains (stubs / in-process tools) — not a cloud multi-agent Runtime.",
    output:
      "Routed or multi-domain synthesis for local exploration; production AWS path still uses Unified only.",
    targetIdHelp:
      "Local sandbox for multi-angle Target ID questions when you want routing across domains; production still consolidates into Unified.",
  },
] as const;

export function getLocalAgent(id: string): LocalAgentOption | undefined {
  return LOCAL_AGENTS.find((a) => a.id === id);
}
