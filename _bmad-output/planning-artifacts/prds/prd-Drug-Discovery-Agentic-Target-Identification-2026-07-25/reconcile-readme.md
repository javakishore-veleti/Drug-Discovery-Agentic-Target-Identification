# Input Reconciliation: README.md → PRD + Addendum

**Date:** 2026-07-25  
**Secondary input:** `README.md` (public positioning + architecture sketch)  
**Primary specs:** `prd.md`, `addendum.md`  
**Purpose:** PRD finalize — extract **gaps only** (missing, diluted, or contradicted README language/contracts). Intentional V1 scope cuts acknowledged in PRD/addendum are **not** gaps.

---

## Summary

| Verdict | Count |
| --- | --- |
| Material gaps | 5 |
| Minor / docs-only gaps | 3 |
| Intentional deferrals (acknowledged) | 12+ tool/catalog items |
| Aligned (no action) | Core architecture path, security boundary, 3-tool V1, demo narrative core, prerequisites |

---

## Material Gaps

### GAP-1: Domain education and pipeline positioning (public copy)

**README (source):**
- Dedicated section **“What is target identification?”** with definition (target = biological molecule linked to disease), typical scientist questions (disease biology, druggability, inhibit/activate effects, patient benefit, patents/competition), and pipeline placement diagram: *Disease biology → Target identification → Target validation → Hit/lead discovery → Optimization → Preclinical → Clinical*.

**PRD + addendum:**
- Glossary defines product terms; Vision describes copilot behavior. No requirement to preserve README’s domain-education block or pipeline diagram in shipped docs/UI.

**Gap type:** Missing public positioning language  
**Risk:** External readers (GitHub landing) get domain context README promises; V1 docs per FR-21 may omit it unless explicitly scoped.  
**Suggested reconcile:** Add to FR-21 consequences or addendum: V1 docs/README must either (a) retain domain-education section with V1-scope qualifier, or (b) README updated at ship to point to PRD-honest scope. PRD should state which.

---

### GAP-2: Unified Research Agent capability taxonomy diluted

**README (source):**
Agent section lists **six** named capability domains:
1. Drug profile analysis (mechanism, **toxicity, PK**)
2. Patient risk assessment (populations, biomarkers)
3. **Molecular pathway mapping (interactions, networks)**
4. Target safety / cardioprotection analysis
5. Drug design hypothesis generation
6. Patent and literature intelligence (where configured)

Key features mirror: profiling/toxicity, risk stratification, **pathway/protein-interaction intelligence**, target safety, design hypotheses.

**PRD + addendum:**
- FR-10: mechanism, safety/patient-risk framing, design hypotheses via three tools + synthesis.
- Assumption (§12): pathway/cardiotoxicity *may* be answered without dedicated pathway/FAERS tools.
- No FR preserves README’s six-domain agent taxonomy or **PK profiling** as a named capability.
- Patent/literature (#6) correctly deferred (Non-Goals, Addendum G/H).

**Gap type:** Diluted public positioning / capability contract  
**Risk:** README still advertises pathway mapping and protein-interaction intelligence as platform capabilities; PRD accepts synthesis-only answers that may be weak for those domains.  
**Suggested reconcile:** FR-21 or Vision addendum: public/agent docs use honest capability framing (“literature/trials/chemistry synthesis; pathway/PK depth limited in V1”) OR README capability list qualified at finalize.

---

### GAP-3: Protein-interaction example query vs V1 tool reality

**README (source):**
- Example query: *“What proteins interact with HER2 in cardiac tissue?”*
- Tool catalog cites **STRING, UniProt, Ensembl, GTEx, GEO** under proteins & genomics.

**PRD + addendum:**
- Canonical demos (Addendum G): mechanism, cardiotoxicity populations, safer-targeting — **no** protein-interaction example.
- FR-16 / Addendum H: STRING, UniProt, etc. deferred.
- FR-10 assumes pathway/cardiotoxicity framing without dedicated pathway tools.

**Gap type:** Contradiction / diluted promise (public examples vs V1)  
**Risk:** README example sets user expectation for interaction/network answers the three-tool slice cannot reliably ground.  
**Suggested reconcile:** Either drop/relabel README example as post-V1, add to Non-Goals “protein-interaction network queries requiring STRING/UniProt,” or add non-canonical demo disclaimer in FR-21.

---

### GAP-4: Gateway tools hosted on Lambda (architecture contract)

**README (source):**
Architecture components table: **Tools | AgentCore Gateway + Lambda | Biomedical database / API access**

**PRD + addendum:**
- FR-18 lists “AgentCore Gateway (MCP)” among building blocks.
- Addendum A diagram: Gateway → PubMed | ClinicalTrials | ChEMBL — **no Lambda** in tool layer.
- Stream Lambda documented; gateway tool compute mechanism unspecified.

**Gap type:** Missing architecture contract  
**Risk:** Downstream architecture may omit README’s Gateway+Lambda pattern without contradicting PRD.  
**Suggested reconcile:** Addendum A or §9.1: Gateway Tools are exposed via AgentCore Gateway with **Lambda-backed** implementations (per README), or explicitly note if V1 diverges.

---

### GAP-5: “Persistent research sessions” vs V1 session boundary

**README (source):**
Key feature: **“Persistent research sessions”** (no qualifier).

**PRD + addendum:**
- FR-17: multi-turn memory **within one Chat Session** only.
- Explicit non-goals: cross-day session resume / session list UI.
- Chat Session glossary: ends on logout/close; no tomorrow resume.

**Gap type:** Diluted / potentially contradictory  
**Risk:** “Persistent” reads as durable cross-session history; PRD limits persistence to single browser session.  
**Suggested reconcile:** Qualify README feature to “multi-turn session memory (same Chat Session)” or add FR-21 docs requirement to define “persistent” consistently.

---

## Minor / Docs-Only Gaps

### GAP-M1: React + TypeScript

**README:** Frontend = **React + TypeScript**  
**PRD:** React chat UI only (§4.2, §6.1) — TypeScript not stated.  
**Severity:** Low — likely implementation default; add to constraints if README is binding.

### GAP-M2: Repository layout contract

**README:** Documents tree: `agents/`, `gateways/database/`, `infra/backend|frontend/`, `web/`, `docs/`.  
**PRD/addendum:** Silent on repo structure.  
**Severity:** Low for PRD product reqs; medium if README layout is an architecture invariant for extensibility (UJ-2 “add tool in a day”).

### GAP-M3: Biomni lineage / acknowledgments

**README:** Acknowledgments credit **Stanford Biomni** database tooling patterns adapted for AgentCore gateway.  
**PRD/addendum:** Biomni named only as competitive context (Addendum E), not attribution requirement.  
**Severity:** Low — public docs/attribution, not functional gap.

---

## Intentional Deferrals (NOT Gaps — PRD Acknowledges)

| README item | PRD / addendum acknowledgment |
| --- | --- |
| 30+ biomedical tools (OpenFDA, PubChem, UniProt, STRING, Ensembl, GTEx, GEO, Reactome, KEGG, PDB, AlphaFold, …) | FR-16, §5 Non-Goals, §6.2, Addendum H |
| USPTO patent tool + `.env` / API key flow | §5 Non-Goals, NFR-3 assumption, Addendum G (patent examples out of V1) |
| Patent example queries | Addendum G |
| Multi-agent / swarm | §5 Non-Goals, §6.2 |
| Enterprise IdP (“or your IdP”) | §2.2 Non-Users, §5 Non-Goals |
| FAERS / heavy safety pipelines | §5 Non-Goals |
| Full tool catalog in architecture diagram (“…”) | Vision “not a 30+ tool suite”; Addendum A lists 3 tools |

---

## Aligned (No Gap)

- **Product hook:** Agentic target identification via Bedrock AgentCore + MCP-style gateway — aligned (Vision, Glossary, Addendum A).
- **Request path:** Researcher → CloudFront/S3 UI → Cognito → Stream Lambda (SSE/SigV4) → AgentCore Runtime → Claude → Gateway → public APIs — aligned; addendum narrows API set appropriately.
- **Security boundary:** Browser must not invoke AgentCore directly; Cognito + signed backend path — aligned (FR-8, NFR-1, README Security notes).
- **Unified Research Agent** naming and multi-domain synthesis intent — aligned at V1 depth.
- **Core demo narrative:** Herceptin / HER2 mechanism, cardiotoxicity/vulnerable populations, safer targeting — aligned (UJ-1, Addendum G); README’s 4th/5th examples partially overlap (patent deferred).
- **Streaming + tool visibility:** Key README features map to FR-4, FR-5.
- **Prerequisites:** Bedrock, CLI, Node 22+, Python 3.12+, Docker, CDK bootstrap — aligned (§10, UJ-2).
- **CDK deploy/destroy lifecycle** — aligned (FR-18–FR-20).
- **Research-assist / not clinical** — aligned (Disclaimer FR-6, FR-12, Addendum F); PRD is **stronger** than README (no disclaimer in README body).
- **Honest V1 slice framing** — PRD explicitly narrows README’s broad “drug discovery platform” claims; FR-21 requires honest scope in docs — aligned intent, see GAP-1/GAP-2 for public copy detail.

---

## Recommended PRD Finalize Actions

1. **FR-21 / docs:** Require README–PRD alignment pass: domain-education block, capability qualifiers, session persistence wording, deferred-tool examples.
2. **Addendum A or §9.1:** State Gateway Tool = Lambda-backed (README contract) or document deliberate change.
3. **Non-Goals or Addendum G:** Explicitly exclude protein-interaction/network queries as V1 acceptance unless answered via literature synthesis only (manage GAP-3).
4. **Optional:** Add TypeScript + repo layout to §9 constraints if README remains canonical for builders.

---

## Reconciliation Metadata

- **Inputs compared:** README.md (340 lines effective), prd.md, addendum.md  
- **Gaps extracted:** 5 material, 3 minor  
- **Deferrals validated:** Tool catalog, USPTO, SSO, multi-agent, FAERS — all acknowledged  
- **Output for finalize:** Address GAP-1–GAP-5 before treating README and PRD as consistent public + requirements pair
