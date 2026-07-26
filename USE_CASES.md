# Use cases — who benefits from Agentic Target ID

Fifty persona-oriented scenarios where the **Unified Research Agent**, Gateway tools (PubMed, ClinicalTrials.gov, ChEMBL, optional Open Targets), Stream Events, and local specialist CLIs help people move faster on **early target identification and evidence synthesis**.

> Research assistance over **public** data. Not medical advice, not clinical decision support, not a validated-target ranking product.

**How to read this:** each item is a realistic “I need to…” moment. Many map to the Herceptin / HER2-style multi-turn demo (mechanism → risk → chemistry/target context).

---

## 1. Discovery biologists & target hunters (pharma / biotech)

1. Sketch disease biology drivers and shortlist protein/gene targets from literature before wet-lab prioritization.
2. Ask whether a pathway node is plausibly druggable given published MoA and chemistry context.
3. Compare two candidate targets for the same indication using literature + trial landscape.
4. Pull Open Targets / Ensembl-style evidence for a gene of interest (with `enableTool4=true`).
5. Trace how a known drug (e.g. trastuzumab) engages its target to reverse-engineer lessons for a new program.
6. Flag on-target vs off-target safety themes early from literature and trial adverse-event narratives.
7. Build a first-pass target rationale outline with PMIDs / NCT / ChEMBL citations ready to paste.
8. Revisit a shelved target after new trials or papers appear, without a week of manual search.

## 2. Translational scientists & biomarker leads

9. Identify patient populations most associated with benefit or risk for a drug–target pair.
10. Link biomarkers (expression, genetics mentions in lit/trials) to target hypothesis strength.
11. Scan interventional trials for enrichment strategies used against the same target class.
12. Ask follow-ups in one Chat Session (“given that MoA, who is most vulnerable to cardiotoxicity?”).
13. Contrast companion-diagnostic themes in literature vs what trials actually enrolled.
14. Prepare translational questions for a KR review with cited public sources, not slide folklore.

## 3. Medicinal chemists & drug design teams

15. Gather ChEMBL context for a marketed antibody or small molecule related to the target.
16. Generate early design hypotheses (modality, binding themes) grounded in public chemistry records.
17. Check what chemical matter / target annotations already exist before committing synthesis cycles.
18. Compare tool compounds in papers with ChEMBL entries for the same target.
19. Use the local **drug-design-hypothesis** CLI to pressure-test “what if we modulate X instead of Y?”
20. Avoid reinventing scaffolds that literature already associates with known liabilities.

## 4. Safety, toxicology & cardioprotection reviewers

21. Front-load cardiac liability questions for HER2-class or other cardiotoxic mechanisms.
22. Use the **cardioprotection-target** specialist locally to frame safer-targeting research questions.
23. Collect literature on organ-system toxicities tied to a target class before in vivo studies.
24. Map trial dropout / AE themes for drugs hitting the same pathway.
25. Brief a safety committee with cited NCT/PMID evidence instead of ad-hoc PubMed tabs.
26. Explore whether an alternative pathway node might reduce on-target toxicity hypotheses.

## 5. Clinical development & medical affairs (pre-IND / early clinical)

27. Inventory ongoing and completed trials for a target or drug class (NCT IDs).
28. Summarize inclusion/exclusion patterns across competitor trials for the same biology.
29. Draft an internal landscape memo for a new indication-expansion idea.
30. Answer medical-science liaison prep questions with public citations (not promotional claims).
31. Spot crowded vs white-space trial activity around a mechanism.
32. Prepare due-diligence questions before licensing a clinical-stage asset.

## 6. Portfolio, BD & competitive intelligence

33. Rapid CI scan: who is running trials against this target, and with what modalities?
34. Compare public evidence depth for two in-licensing candidates overnight.
35. Stress-test a partner’s target story against PubMed + ClinicalTrials + ChEMBL in one session.
36. Flag when a “novel” target already has extensive negative trial history.
37. Support kill/continue portfolio debates with transparent tool-use traces (Stream Events).
38. Educate non-scientist BD stakeholders with a short, cited mechanism narrative.

## 7. Academic PIs, postdocs & grad students

39. Orient a new lab member to a target/disease area with guided, tool-backed Q&A.
40. Find seminal PMIDs and recent reviews before writing grant specific aims.
41. Check whether a thesis hypothesis already failed in registered trials.
42. Generate a reading list + ID set (PMID/NCT/ChEMBL) for journal club.
43. Explore cross-disciplinary angles (chem + trials + genetics mentions) without mastering every database UI.
44. Teach a methods class how agentic tool use differs from a single LLM hallucination.

## 8. Bioinformatics & computational biology collaborators

45. Bootstrap gene/target IDs (Ensembl via Open Targets) before building internal pipelines.
46. Validate that a computational hit has any human trial or chemistry footprint.
47. Produce a citation-backed narrative to hand to wet-lab partners alongside a ranked gene list.
48. Prototype “ask the public graph” before investing in a private knowledge graph.
49. Wrap additional biomedical APIs using the same Gateway timeout / 429 / `status: error` contract.

## 9. Platform / ML engineers & AWS / AI learners

50. Demo Bedrock AgentCore (Runtime + Gateway + Memory), Cognito → SigV4 Stream Events, BMAD specs, golden evals, and optional tool #4—on a real scientific vertical (stakeholder workshop, team lab, or MIT portfolio fork).

---

## Quick map: persona → product surface

| Persona | Usually starts with | Tools that help most |
| --- | --- | --- |
| Discovery / translational | Mechanism & population questions | pubmed, clinicaltrials, opentargets |
| Chemistry / design | “What matter exists for…?” | chembl, pubmed |
| Safety | Toxicity & organ risk | pubmed, clinicaltrials (+ cardioprotection CLI) |
| BD / CI | Landscape & crowding | clinicaltrials, pubmed |
| Engineers / learners | Architecture & demos | full stack + evals/ops docs |

## Out of scope (do not treat as use cases)

- Prescribing, dosing, or patient-specific treatment decisions  
- Claiming a target is “validated” or investment-grade solely from this agent  
- Replacing proprietary competitive intel, closed literature, or regulated clinical systems  
