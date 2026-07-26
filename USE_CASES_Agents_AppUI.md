# Use cases → persona, agent, App UI / CLI prompts

Companion to [`USE_CASES.md`](USE_CASES.md). For each of the **50** scenarios: **persona**, **where to run**, **which agent(s)**, and **example prompt(s)** (one or more).

> Research assistance only — not medical advice or clinical decision support. Prefer **cited** answers (PMID / NCT / ChEMBL / Ensembl).  
> **Open Targets** prompts need deploy with `-c enableTool4=true`.

### Surfaces & agents

| Surface | Agent | How to use |
| --- | --- | --- |
| **App UI** (recommended) | **Unified Research Agent** | Cognito login → research chat (Stream Events show `tool_use`) |
| Local CLI | `drug-profile-analysis-agent` | MoA / toxicity / PK framing |
| Local CLI | `patient-risk-assessment-agent` | Population / risk signals |
| Local CLI | `pathway-mapping-agent` | Pathway / network literature framing |
| Local CLI | `cardioprotection-target-agent` | Cardiac safety / cardioprotection |
| Local CLI | `drug-design-hypothesis-agent` | Design / chemistry hypotheses |
| Local CLI | `genetic-risk-assessment` | Genetics research framing (stub tools) |
| Local CLI | `medical-supervisor-agent` | Local router demo only — **not** cloud multi-agent |

**Default for almost all rows:** App UI → Unified Research Agent. Local CLIs are optional for domain-focused iteration without redeploying Runtime.

---

## 1–8 · Discovery biologists & target hunters

| # | Persona | Use case | Surface / agent(s) | Example prompt(s) |
| ---: | --- | --- | --- | --- |
| 1 | Discovery biologist | Shortlist targets from disease biology literature | **App UI** · Unified Research Agent · *(opt.)* pathway-mapping CLI | `Summarize disease biology drivers for HER2-positive breast cancer and shortlist protein/gene targets cited in recent literature. Cite PMIDs.` · `Which targets appear most often linked to this indication in PubMed? List gene symbols and PMIDs.` |
| 2 | Discovery biologist | Is a pathway node plausibly druggable? | **App UI** · Unified · *(opt.)* drug-profile + chembl via agent | `Is HER2/ERBB2 considered druggable based on published MoA and chemistry context? Cite PMID and ChEMBL IDs.` · `What modalities have successfully modulated ERBB2 in the clinic or literature?` |
| 3 | Target hunter | Compare two candidate targets | **App UI** · Unified | `Compare ERBB2 vs EGFR as targets in breast cancer: literature strength, trial activity (NCT IDs), and chemistry footprint (ChEMBL). Table the differences.` · `For the same indication, which of PI3K vs HER2 has denser negative trial history? Cite NCTs.` |
| 4 | Target hunter | Open Targets / Ensembl evidence | **App UI** · Unified *(tool4)* · *(opt.)* genetic-risk CLI | `Use Open Targets to find ERBB2/HER2 target evidence and cite Ensembl IDs.` · `What disease associations does Open Targets report for ERBB2? Summarize with Ensembl id.` |
| 5 | Discovery biologist | Reverse-engineer lessons from a known drug | **App UI** · Unified · *(opt.)* drug-profile CLI | `What is the mechanism of action of Herceptin (trastuzumab)? Cite PMIDs and any ChEMBL ids.` · `What target-engagement lessons from trastuzumab apply to designing a next-gen HER2 program?` |
| 6 | Discovery / safety-aware biologist | On- vs off-target safety themes | **App UI** · Unified · *(opt.)* patient-risk CLI | `From literature and trials, what on-target vs off-target safety themes are reported for HER2-targeted agents? Cite PMID/NCT.` · `Which adverse events appear most linked to HER2 pathway drugs in ClinicalTrials.gov summaries?` |
| 7 | Discovery biologist | First-pass target rationale with IDs | **App UI** · Unified | `Draft a one-page target rationale for ERBB2 in HER2+ breast cancer. Include bullet evidence with PMID, NCT, and ChEMBL citations where available.` · `List 5 must-cite papers (PMIDs) and 3 key trials (NCTs) for an ERBB2 target brief.` |
| 8 | Discovery biologist | Revisit a shelved target | **App UI** · Unified *(tool4 helpful)* | `What new PubMed papers and ClinicalTrials.gov studies since 2020 mention ERBB2 as a therapeutic target in gastric cancer? Cite IDs.` · `Has Open Targets evidence for ERBB2 changed the case for revisiting this target in a new indication?` |

---

## 9–14 · Translational scientists & biomarker leads

| # | Persona | Use case | Surface / agent(s) | Example prompt(s) |
| ---: | --- | --- | --- | --- |
| 9 | Translational scientist | Populations tied to benefit/risk | **App UI** · Unified · *(opt.)* patient-risk CLI | `Which patient populations are most associated with benefit or cardiotoxicity risk for trastuzumab? Cite PMID/NCT.` · `Are elderly or cardiac-comorbid patients called out in HER2 trial literature for higher risk?` |
| 10 | Biomarker lead | Biomarkers ↔ target hypothesis | **App UI** · Unified *(tool4 helpful)* · *(opt.)* genetic-risk CLI | `What biomarkers (IHC, FISH, expression, genetics) are used to select patients for HER2-targeted therapy? Cite PMIDs/NCTs.` · `Does Open Targets list genetic evidence linking ERBB2 to breast cancer? Cite Ensembl id.` |
| 11 | Translational scientist | Enrichment strategies in trials | **App UI** · Unified | `Scan ClinicalTrials.gov for interventional HER2 trials that use biomarker enrichment. Summarize strategies and cite NCT IDs.` · `What inclusion criteria patterns recur in Phase 2/3 trastuzumab or HER2-ADC trials?` |
| 12 | Translational scientist | Multi-turn follow-up (same session) | **App UI** · Unified *(same Chat Session)* | *Turn 1:* `What is the mechanism of action of Herceptin?` · *Turn 2:* `Given that MoA, which patient populations are most vulnerable to its cardiotoxicity? Cite sources.` |
| 13 | Biomarker / CDx-aware lead | Lit CDx themes vs trial enrollment | **App UI** · Unified | `Contrast companion-diagnostic themes in HER2 literature with what trials actually required for enrollment. Cite PMID vs NCT.` · `Which HER2 trials enrolled based on IHC vs FISH vs both? Give NCT examples.` |
| 14 | Translational scientist | KR review question list | **App UI** · Unified | `Prepare 8 translational due-diligence questions for an ERBB2 program KR, each backed by at least one PMID or NCT you found.` · `What open questions remain about HER2 cardiotoxicity mechanisms in the public literature?` |

---

## 15–20 · Medicinal chemists & drug design

| # | Persona | Use case | Surface / agent(s) | Example prompt(s) |
| ---: | --- | --- | --- | --- |
| 15 | Medicinal chemist | ChEMBL context for a drug | **App UI** · Unified · *(opt.)* drug-profile CLI | `What ChEMBL context exists for trastuzumab / HER2-targeted agents? Cite ChEMBL IDs.` · `Find ChEMBL entries related to ERBB2 and summarize target annotations.` |
| 16 | Drug design scientist | Early design hypotheses | **App UI** · Unified · **or** drug-design-hypothesis CLI | `Based on public chemistry and literature, propose 3 early design hypotheses for modulating HER2 with fewer cardiac liabilities. Cite ChEMBL/PMID.` · `What modalities (mAb, ADC, TKI, bispecific) dominate HER2 chemical/clinical matter?` |
| 17 | Medicinal chemist | Existing chemical matter check | **App UI** · Unified | `Before we start synthesis: what chemical matter and target annotations already exist in ChEMBL for ERBB2?` · `List representative ChEMBL compound/target links for HER2 inhibitors or antibodies.` |
| 18 | Medicinal chemist | Tool compounds vs ChEMBL | **App UI** · Unified | `Which tool compounds are commonly used in HER2 literature, and can you match them to ChEMBL IDs?` · `Compare published HER2 TKIs mentioned in PubMed with ChEMBL records.` |
| 19 | Drug design scientist | Pressure-test modulate X vs Y | **Local CLI** · drug-design-hypothesis · *(also)* App UI Unified | `What if we modulate EGFR instead of ERBB2 for the same breast cancer setting—what does public chem/lit suggest for selectivity and risk?` · `Hypothesize a dual-target strategy and list evidence gaps with PMIDs.` |
| 20 | Medicinal chemist | Avoid liability-linked scaffolds | **App UI** · Unified · *(opt.)* drug-design-hypothesis CLI | `Which scaffolds or drug classes against HER2/EGFR are repeatedly associated with safety liabilities in literature? Cite PMIDs.` · `What chemistry-related warnings appear for HER2 TKIs in public sources?` |

---

## 21–26 · Safety, toxicology & cardioprotection

| # | Persona | Use case | Surface / agent(s) | Example prompt(s) |
| ---: | --- | --- | --- | --- |
| 21 | Safety scientist | Cardiac liability front-load | **App UI** · Unified · *(opt.)* cardioprotection CLI | `What cardiac liabilities are reported for HER2-targeted therapies? Cite PMID and NCT.` · `Summarize proposed mechanisms of trastuzumab-related cardiotoxicity from PubMed.` |
| 22 | Cardioprotection reviewer | Safer-targeting research questions | **Local CLI** · cardioprotection-target-agent · *(also)* App UI | `Frame research questions for safer HER2 targeting or cardioprotection strategies, grounded in public literature. Cite PMIDs.` · `What cardioprotective approaches have been studied alongside HER2 therapy in trials? Cite NCTs.` |
| 23 | Toxicologist | Organ-system toxicities for a class | **App UI** · Unified | `What organ-system toxicities are tied to HER2 pathway drugs in literature before in vivo work? Cite PMIDs.` · `Beyond cardiac, what AE themes appear for trastuzumab or HER2 ADCs?` |
| 24 | Safety scientist | Trial AE / dropout themes | **App UI** · Unified | `Map adverse-event and discontinuation themes in ClinicalTrials.gov for HER2-targeted agents. Cite NCT IDs.` · `Which HER2 trials explicitly list LVEF decline or heart failure in outcomes?` |
| 25 | Safety committee briefer | Cited briefing pack | **App UI** · Unified | `Create a short safety briefing on HER2 cardiotoxicity with bullet claims each tied to PMID or NCT.` · `List the top 5 papers and 5 trials a safety committee should review for trastuzumab cardiac risk.` |
| 26 | Safety / discovery partner | Alternative pathway node | **App UI** · Unified · *(opt.)* pathway-mapping CLI | `Could modulating a node downstream or parallel to HER2 reduce on-target toxicity hypotheses? What does literature say? Cite PMIDs.` · `Compare toxicity narratives for HER2 mAbs vs HER2 TKIs.` |

---

## 27–32 · Clinical development & medical affairs

| # | Persona | Use case | Surface / agent(s) | Example prompt(s) |
| ---: | --- | --- | --- | --- |
| 27 | Clinical scientist | Trial inventory | **App UI** · Unified | `Inventory ongoing and completed interventional trials for HER2-positive breast cancer involving trastuzumab or HER2 ADCs. Cite NCT IDs and phases.` · `How many active Phase 3 HER2 trials appear for gastric cancer? List NCTs.` |
| 28 | Clinical development | Inclusion/exclusion patterns | **App UI** · Unified | `Summarize recurring inclusion/exclusion criteria across competitor HER2 trials. Cite example NCTs.` · `Do HER2 trials commonly exclude baseline cardiac dysfunction? Give NCT examples.` |
| 29 | Medical affairs / clindev | Indication-expansion landscape memo | **App UI** · Unified | `Draft an internal landscape memo for expanding a HER2 program into a new solid tumor—use only public lit/trials. Cite IDs.` · `What evidence exists for HER2 therapy in NSCLC or colorectal settings? PMID/NCT.` |
| 30 | MSL / medical affairs | Prep Q&A with citations | **App UI** · Unified | `Prepare non-promotional, citation-backed answers to: MoA of trastuzumab; key efficacy trials; known cardiac risks.` · `What is fair to say from public sources about HER2 testing requirements? Cite PMIDs.` |
| 31 | Clindev strategist | Crowded vs white space | **App UI** · Unified | `Is the HER2 ADC trial landscape crowded in breast vs other tumors? Cite NCT counts/examples.` · `Where does public trial activity look thinner for ERBB2-targeted approaches?` |
| 32 | Clindev / BD partner | Licensing diligence questions | **App UI** · Unified | `Generate due-diligence questions before licensing a clinical-stage HER2 asset, each tied to a gap you see in public NCT/PMID evidence.` · `What public red flags exist for cardiotoxicity management in HER2 programs?` |

---

## 33–38 · Portfolio, BD & competitive intelligence

| # | Persona | Use case | Surface / agent(s) | Example prompt(s) |
| ---: | --- | --- | --- | --- |
| 33 | CI analyst | Who is running trials / modalities | **App UI** · Unified | `Who appears to be running interventional trials against HER2/ERBB2, and with which modalities? Cite NCTs.` · `List recent HER2 bispecific or ADC trials with NCT IDs.` |
| 34 | BD analyst | Compare two in-licensing candidates | **App UI** · Unified | `Compare public evidence depth for trastuzumab vs a HER2 TKI class: trials (NCT), literature (PMID), chemistry (ChEMBL).` · `Overnight CI: summarize public risk/benefit narrative for two HER2 modalities.` |
| 35 | BD / CI | Stress-test partner target story | **App UI** · Unified *(watch Stream `tool_use`)* | `Stress-test this claim using PubMed, ClinicalTrials.gov, and ChEMBL: “ERBB2 is an underserved target with little clinical precedent.” Cite IDs that support or refute.` · `What contradictory evidence exists against a partner’s HER2 novelty narrative?` |
| 36 | Portfolio manager | Negative trial history for “novel” target | **App UI** · Unified | `Has this target class already seen extensive negative or terminated trials? Summarize with NCT IDs.` · `Find terminated or withdrawn HER2-related trials and note stated reasons if available.` |
| 37 | Portfolio / leadership | Kill/continue with tool-use transparency | **App UI** · Unified *(show Stream Events)* | `Give a balanced kill/continue evidence memo for a HER2 follow-on program using only public sources. Show which tools you used.` · `What would change your confidence if Open Targets genetic evidence were weak vs strong?` *(tool4)* |
| 38 | BD (non-scientist stakeholder) | Short cited mechanism narrative | **App UI** · Unified · *(opt.)* drug-profile CLI | `In plain language for BD: how does Herceptin work, why HER2 matters, and what cardiac risk is publicly known? Cite 3 PMIDs.` · `One-paragraph elevator narrative of ERBB2 as a target with citations.` |

---

## 39–44 · Academic PIs, postdocs & grad students

| # | Persona | Use case | Surface / agent(s) | Example prompt(s) |
| ---: | --- | --- | --- | --- |
| 39 | PI / lab mentor | Orient a new lab member | **App UI** · Unified | `Explain HER2/ERBB2 as a therapeutic target for a new grad student: biology, key drugs, open questions. Cite PMIDs.` · `What should I read first (10 PMIDs) to join a HER2 resistance project?` |
| 40 | Postdoc / grant writer | Seminal papers for aims | **App UI** · Unified | `Find seminal and recent review PMIDs on HER2-targeted therapy for a grant specific-aims page.` · `Which papers established trastuzumab MoA and clinical benefit? Cite PMIDs.` |
| 41 | Grad student | Did my thesis idea already fail in trials? | **App UI** · Unified | `Have registered trials already tested inhibiting pathway X for indication Y? List NCTs and outcomes if available.` · `Search ClinicalTrials.gov for failed or terminated HER2 combinations in metastatic breast cancer.` |
| 42 | Journal club lead | Reading list + ID set | **App UI** · Unified | `Generate a journal-club pack: 8 PMIDs, 3 NCTs, and any ChEMBL ids for HER2 ADC recent advances.` · `One-page reading list on trastuzumab cardiotoxicity with IDs.` |
| 43 | Student / interdisciplinary researcher | Cross-domain without every DB UI | **App UI** · Unified *(tool4 helpful)* | `Connect chemistry (ChEMBL), trials (NCT), and genetics/Open Targets for ERBB2 in one summary.` · `What public evidence links ERBB2 genetics to drug response hypotheses?` |
| 44 | Course instructor | Teach agentic tool use vs hallucination | **App UI** · Unified *(show `tool_use` events)* | `Answer using tools only: mechanism of Herceptin with PMIDs. If a tool fails, say so.` · `Same question without tools—then compare why citations differ.` *(instructor contrasts)* |

---

## 45–49 · Bioinformatics & computational biology

| # | Persona | Use case | Surface / agent(s) | Example prompt(s) |
| ---: | --- | --- | --- | --- |
| 45 | Bioinformatician | Bootstrap gene/target IDs | **App UI** · Unified *(tool4)* · *(opt.)* genetic-risk CLI | `Resolve HER2/ERBB2 to Ensembl and related identifiers via Open Targets. Return ids and short evidence summary.` · `What synonyms and target ids should I use for ERBB2 in downstream pipelines?` |
| 46 | Computational biologist | Validate hit has trial/chem footprint | **App UI** · Unified | `I have a computational hit gene SYMBOL—does it have human trial (NCT) or ChEMBL footprint? Summarize.` · `For ERBB2, quantify public trial vs chemistry evidence density.` |
| 47 | Comp bio → wet-lab handoff | Citation-backed narrative + gene list | **App UI** · Unified | `Given ranked genes ERBB2, EGFR, PIK3CA: write a wet-lab handoff narrative with PMID/NCT/ChEMBL per gene.` · `Which of these genes has the strongest public clinical precedent? Cite NCTs.` |
| 48 | Platform-minded bioinformatician | “Ask the public graph” prototype | **App UI** · Unified *(tool4)* | `Using only Gateway tools, answer: is ERBB2 supported as a target in breast cancer across lit, trials, chemistry, and Open Targets?` · `Where are the biggest evidence gaps if we only trust public APIs?` |
| 49 | Platform / tools engineer (bio side) | Same error contract for new APIs | **App UI** demo + **code** (Gateway pattern) · Unified for smoke | *Prompt smoke:* `Call pubmed for ERBB2 reviews and show structured citations.` · *Eng task:* implement next tool Lambda with shared `status: error` / timeout / 429 contract (`docs/tool-4-candidate.md`, `gateways/database/`). |

---

## 50 · Platform / ML engineers & learners

| # | Persona | Use case | Surface / agent(s) | Example prompt(s) |
| ---: | --- | --- | --- | --- |
| 50 | Platform / ML engineer or AWS learner | Full-stack agentic demo | **App UI** · Unified Research Agent · confirm Stream Events · optional tool4 · local specialist CLI optional · evals via `docs/evals.md` | *Demo script:* (1) `What is the mechanism of action of Herceptin?` → watch `tool_use` for pubmed/chembl. (2) Same session: `Which patient populations are most vulnerable to its cardiotoxicity?` (3) If tool4 on: `Use Open Targets for ERBB2/HER2 and cite Ensembl ids.` (4) Optional local: run `drug-profile-analysis-agent` with the MoA prompt. (5) Point stakeholders at BMAD artifacts + golden evals dry-run. |

---

## Multi-turn App UI recipe (Herceptin demo)

Use **one Chat Session** on App UI → Unified Research Agent:

| Step | Prompt |
| ---: | --- |
| 1 | What is the mechanism of action of Herceptin? |
| 2 | Given that, which patient populations are most vulnerable to its cardiotoxicity? Cite PMID/NCT. |
| 3 | What ChEMBL context exists for trastuzumab / HER2-targeted agents? |
| 4 | *(tool4)* Use Open Targets to summarize ERBB2 target evidence and Ensembl id. |

## Quick agent chooser

| If you care about… | Prefer |
| --- | --- |
| Production path, citations, Stream Events | **App UI → Unified Research Agent** |
| MoA / PK framing offline | `drug-profile-analysis-agent` |
| Population risk wording | `patient-risk-assessment-agent` |
| Pathway framing | `pathway-mapping-agent` |
| Cardiac safety questions | `cardioprotection-target-agent` |
| Design hypotheses | `drug-design-hypothesis-agent` |
| Genetics framing (local) | `genetic-risk-assessment` |
