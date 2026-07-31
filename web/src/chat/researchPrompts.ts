/** Example prompts keyed by local agentId (must match localAgents.ts). */

export const PROMPTS_BY_AGENT: Record<string, readonly string[]> = {
  unified: [
    "What is the mechanism of action of Herceptin, and which cardiac safety signals should Target ID consider?",
    "Summarize evidence that HER2 is a valid oncology target, including pathway and population context.",
    "Compare trastuzumab, T-DM1, and T-DXd for HER2 targeting — MoA and key safety differences.",
    "What PubMed and trial evidence links KRAS G12C to NSCLC, and what Target ID questions remain open?",
    "For EGFR in NSCLC: MoA of osimertinib, resistance themes, and biomarker-defined populations.",
    "Is BCL2 a strong hematologic target? Cite literature, trials, and ChEMBL chemistry context.",
    "Map PD-1/PD-L1 biology to Target ID decisions: pathway role, biomarkers, and safety themes.",
    "What evidence supports PCSK9 as a cardiovascular drug target, and what safety trade-offs appear?",
    "For BRCA1-related oncology targets: literature co-mentions, trial landscape, and design hypotheses.",
    "Synthesize FGFR2 fusion evidence as an oncogenic driver and assess druggability signals.",
  ],

  "drug-profile": [
    "What is the mechanism of action of Herceptin (trastuzumab) at the HER2 receptor?",
    "Summarize toxicity and adverse-effect signals reported for trastuzumab in public literature.",
    "What high-level ADME / pharmacokinetics context exists for trastuzumab or related HER2 ADCs?",
    "Compare mechanisms of osimertinib versus earlier-generation EGFR TKIs.",
    "What is the mechanism of action of venetoclax, and what BCL2 target biology supports it?",
    "What safety signals are reported for CDK4/6 inhibitors in breast cancer?",
    "Find ChEMBL bioactivity context for trastuzumab and related HER2-directed agents.",
    "Summarize resistance mechanisms to imatinib in CML from a drug-profile perspective.",
    "What is known about BCL2 as a drug target in hematologic malignancies?",
    "Profile pembrolizumab: MoA (PD-1) and major published safety themes.",
  ],

  "patient-risk": [
    "Which patient populations are most vulnerable to Herceptin cardiotoxicity in published evidence?",
    "What biomarkers predict response to pembrolizumab in NSCLC?",
    "Which populations are underrepresented in Alzheimer’s disease drug trials?",
    "What clinical trials have evaluated trastuzumab in HER2-positive breast cancer, and who was enrolled?",
    "Summarize population stratification themes for EGFR TKI therapy in NSCLC.",
    "What adverse-event patterns are reported for CDK4/6 inhibitors across trial populations?",
    "Which biomarkers are used to select HER2-targeted therapy in breast or gastric cancer?",
    "What trial evidence describes cardiotoxicity risk groups for HER2-directed antibodies?",
    "For KRAS G12C inhibitors, which patient subgroups appear in published trial reports?",
    "What population-level safety signals are reported for TNF-alpha inhibitors across indications?",
  ],

  "pathway-mapping": [
    "Map HER2/ERBB2 signaling pathways relevant to trastuzumab’s mechanism of action.",
    "What is the biological role of PD-1 / PD-L1 in tumor immune evasion pathways?",
    "Summarize PI3K/AKT and MAPK pathway context for HER2-driven breast cancer.",
    "How do EGFR signaling pathways differ across generations of EGFR TKIs?",
    "What pathway relationships link BRCA1 to DNA-repair targets discussed in oncology literature?",
    "Map BCL2’s role in apoptotic pathways relevant to venetoclax.",
    "What is known about FGFR2 fusion-driven signaling as an oncogenic pathway?",
    "Summarize IL-6 / IL-6R pathway biology as autoimmune drug-target context.",
    "How does CTLA-4 blockade fit into T-cell checkpoint pathways with PD-1?",
    "Describe pathway redundancy risks when targeting HER2 — what parallel nodes are discussed?",
  ],

  cardioprotection: [
    "Which patient populations are most vulnerable to Herceptin cardiotoxicity?",
    "What mechanisms are proposed for trastuzumab-related cardiotoxicity in the literature?",
    "Summarize cardiotoxicity signals for HER2-targeted therapies (antibodies and ADCs).",
    "What evidence discusses cardioprotection strategies or hypotheses around HER2 blockade?",
    "Find literature on trastuzumab-induced cardiac dysfunction versus anthracycline cardiotoxicity.",
    "What cardiac safety themes appear for CDK4/6 inhibitors or other breast-cancer targeted agents?",
    "Summarize cardiovascular outcome literature for GLP-1 receptor agonists (research framing only).",
    "What is known about HER2/ErbB2 signaling in cardiomyocytes relevant to on-target cardiac risk?",
    "Compare published cardiac safety signals across trastuzumab, T-DM1, and T-DXd.",
    "What trial endpoints or cardiac monitoring themes are reported for HER2 agents (research only)?",
  ],

  "drug-design": [
    "Find ChEMBL bioactivity data for compounds targeting EGFR.",
    "What ChEMBL records and related agents exist for trastuzumab / HER2-directed ADCs?",
    "What ChEMBL assays exist for JAK2 inhibitors?",
    "Propose selectivity / off-target hypotheses for EGFR TKIs grounded in ChEMBL and literature.",
    "What chemistry context supports optimizing HER2-targeted ADCs (payload / linker themes in literature)?",
    "Summarize ChEMBL and literature for BCL2 inhibitors related to venetoclax-like mechanisms.",
    "What public chemistry evidence informs safer targeting hypotheses for kinase inhibitors?",
    "Compare ChEMBL bioactivity context for osimertinib versus earlier EGFR TKIs.",
    "Which ChEMBL entities are associated with FGFR2-targeted approaches?",
    "Ground a design hypothesis for PD-1/PD-L1 modulators in published chemistry/literature (no invented docking).",
  ],

  "genetic-risk": [
    "Summarize PubMed evidence linking KRAS G12C to non-small cell lung cancer.",
    "What genetic / gene-level evidence supports ERBB2 (HER2) as an oncology target?",
    "Which genetic variants affect warfarin dosing, and what is the supporting evidence?",
    "What is known about FGFR2 fusions as oncogenic drivers?",
    "Summarize BRCA1-related genetic context for DNA-repair targeted therapy research.",
    "What literature links EGFR mutations to TKI selection in NSCLC?",
    "Find reviews on how germline or somatic genetics inform early target identification (research only).",
    "What gene–disease association themes for PCSK9 appear in cardiovascular literature?",
    "Summarize genetic evidence themes for BCL2 in hematologic malignancies.",
    "What published genetic context supports CTLA-4 / immune-checkpoint pathway targeting?",
  ],

  "medical-supervisor": [
    "Coordinate a multi-domain Target ID brief on Herceptin: MoA, populations at cardiac risk, and pathway context.",
    "Route and synthesize: is HER2 still a strong target given efficacy, cardiac safety, and ADC chemistry?",
    "For EGFR in NSCLC, cover drug profile, resistance pathways, and biomarker-defined populations.",
    "Multi-domain view of BCL2: mechanism, genetics/hematology context, and design/chemistry signals.",
    "Synthesize PD-1/PD-L1 Target ID: pathway biology, biomarkers, and safety themes from public sources.",
    "Cross-domain brief on KRAS G12C: genetics, pathway, trials, and chemistry/druggability notes.",
    "Supervisor-style synthesis: trastuzumab cardiotoxicity — who is vulnerable and what mechanisms are proposed?",
    "Multi-angle Target ID on PCSK9: disease biology, genetics themes, and cardiovascular evidence.",
    "Coordinate pathway + drug-profile view of FGFR2 fusions as oncogenic drivers.",
    "Synthesize a Target ID memo on CDK4/6 inhibitors: MoA, population AE patterns, and open questions.",
  ],
};

export function promptsForAgent(agentId: string): readonly string[] {
  return PROMPTS_BY_AGENT[agentId] ?? PROMPTS_BY_AGENT.unified;
}
