---
title: "Input Reconciliation: Product Brief → PRD"
input: brief-Drug-Discovery-Agentic-Target-Identification-2026-07-25/brief.md
compared_against:
  - prd.md
  - addendum.md
created: 2026-07-25
---

# Reconciliation: Finalized Product Brief vs PRD + Addendum

**Direction:** Brief is source of truth for intent. This document lists **gaps only** — brief ideas that are missing, diluted, or contradicted in `prd.md` and `addendum.md`. Items already well preserved (auth, streaming, Herceptin demo, CDK lifecycle, honest scope, competitive do-not-claim table, post-V1 Open Targets preference) are omitted.

---

## 1. Problem narrative and qualitative stakes — **missing**

**Brief carries:**
- Target ID sits early in the pipeline and absorbs disproportionate cost and failure risk.
- Evidence is scattered across literature, trial registries, chemistry DBs, protein networks, and safety sources; scientists stitch answers by hand.
- Multi-domain questions (Herceptin mechanism → cardiotoxicity → pathway context → safer targeting) take **hours** of fragmented search with **weak source traceability**.
- Alternatives **overwhelm with breadth**, **lock into licensed graphs/enterprise contracts**, or stop at **static data portals**.
- The gap is explicitly for teams **and for builders learning AgentCore** — a governed, forkable vertical slice without fake “enterprise validated” claims.

**PRD/addendum:**
- No dedicated problem section. Pain is implied only through Asha’s JTBD (“without hand-stitching PubMed…”) and competitive notes in addendum §E.
- The **industry pain story**, **time cost**, **fragmentation**, and **anti-lock-in / anti-theater** framing from the brief do not appear in Vision, Document Purpose, or positioning language.

**Gap type:** Missing qualitative context that explains *why* the slice matters beyond feature checklist. FR structure silently drops the brief’s problem voice.

**Suggested carry-forward (polish):** One short “Problem / Context” subsection in PRD §1 or §0 — even 3–4 sentences — preserving brief tone: scattered evidence, hours lost, weak traceability, alternatives that overwhelm or lock in, gap for scientists *and* AgentCore learners.

---

## 2. “Pathway context” as a named demo and synthesis pillar — **diluted**

**Brief carries:**
- Executive summary: agent synthesizes evidence on **mechanism, safety, pathways, patient risk, and design hypotheses**.
- Solution: V1 Herceptin demo explicitly includes **pathway context** alongside mechanism, cardiotoxicity, and safer-targeting hypotheses.
- Example question chain ends with **pathway context** before safer targeting.

**PRD/addendum:**
- FR-10 lists mechanism, safety / patient-risk framing, and design hypotheses — **pathways not named**.
- Canonical demo prompts (addendum §G) cover mechanism, cardiotoxicity populations, safer targeting — **no pathway-oriented prompt or acceptance consequence**.
- `[ASSUMPTION]` in PRD §12 notes pathway/cardiotoxicity *may* be answered from existing tools — treats pathway as implementation assumption, not a brief-mandated demo dimension.

**Gap type:** Dilution. Pathway is a first-class brief synthesis domain and demo beat; PRD folds related content under safety/design without preserving “pathway context” as explicit scope or demo narrative.

**Suggested carry-forward:** Add “pathway context (model-synthesized from literature/trials/chemistry; no dedicated pathway DB in V1)” to FR-10 consequences and/or addendum §G demo prompt; align executive Vision bullet with brief’s five synthesis domains.

---

## 3. Gateway tool count **3–5** (brief) vs **exactly 3** (PRD) — **contradicted**

**Brief carries:**
- Scope: “AgentCore Gateway with **3–5** tools: PubMed, ClinicalTrials.gov, ChEMBL first.”
- Success metric: “At least **3** tools callable” (minimum, not maximum).

**PRD/addendum:**
- FR-16: “V1 ships **exactly** these three Gateway Tools.”
- SM-2: “**Exactly 3** Gateway Tools”; SM-C1 counter-metric: “Do not expand past 3.”
- Addendum §I: “Tools 4–5 in the default deploy” rejected.

**Gap type:** Contradiction on upper bound. PRD chose a deliberate narrow slice (good for shippability) but **overrides** brief’s explicit 3–5 range without documenting the decision as a brief deviation.

**Suggested carry-forward:** Either (a) restore brief alignment with “minimum 3, up to 5 if ready” in MVP scope, or (b) add explicit PRD note: “Brief allowed 3–5; V1 locked to 3 per SM-C1 — tools 4–5 deferred.” Log in memlog if intentional scope cut.

---

## 4. Positioning language: “governed,” “productized,” “discovery desk research” — **diluted**

**Brief carries (tone / feel):**
- “**Governed**, forkable, AWS-native vertical slice”
- “**Productized desk research** for target exploration”
- “AWS-native **governed research copilot**”
- “**Forkable discovery desk research**” — not BenchSci / Insilico-grade validated platform

**PRD/addendum:**
- Technical “governance shape” (browser never invokes AgentCore directly) — present.
- “Research assistance,” “forkable AWS life-sciences research-agent slice,” “honest scope language” — present but **generic**.
- Brief’s distinctive identity phrases — **governed**, **productized**, **discovery desk research** — do not appear in Vision, MVP scope, or docs/branding requirements (FR-21 mentions “professional docs and branding” but not brief positioning vocabulary).

**Gap type:** Qualitative positioning diluted. The product *feel* in the brief is “governed, honest, forkable desk research”; PRD reads as “demoware vertical slice with security boundary.” Same bones, weaker voice.

**Suggested carry-forward:** Preserve brief phrases in PRD §1 Vision closing, FR-21 docs consequence, and/or addendum §E competitive stance — especially “productized desk research” and “governed research copilot (not validated-target platform).”

---

## 5. Multi-domain demo as one connected research thread — **diluted**

**Brief carries:**
- A **single flowing narrative**: one Herceptin session that moves mechanism → cardiotoxicity risk → pathway context → safer targeting ideas — illustrating multi-domain synthesis as the product’s “aha,” not three isolated Q&A slots.

**PRD/addendum:**
- UJ-1 walks mechanism then one follow-up on cardiotoxicity — good but **stops short** of the full brief chain.
- Addendum §G lists three **discrete** canonical prompts with no guidance that the demo should feel like one connected exploration arc.
- No success metric or journey climax tied to **cross-domain continuity** beyond one follow-up (SM-3).

**Gap type:** Dilution of demo *feel*. Brief sells integrated desk research; PRD validates isolated turns + one follow-up.

**Suggested carry-forward:** Extend UJ-1 or add SM/demo note: optional third turn (pathway or safer-targeting) in same session; document recommended demo script as a **sequence**, not a menu of unrelated prompts.

---

## 6. Long-term vision: composable pattern, transparent synthesis, humans in the loop — **diluted**

**Brief carries (Vision):**
- Near-term: Open Targets–style evidence/pathway tools before multi-agent — **aligned** in PRD §6.2 and addendum §H.
- **2–3 years:** “Composable AWS life-sciences **research agent pattern**”; fork the slice, plug tools via MCP; **keep evidence synthesis transparent**; public-API-first desk research with **humans in the loop**.

**PRD/addendum:**
- Post-V1 tool roadmap captured.
- **Missing:** 2–3 year horizon, “composable pattern” framing, “transparent evidence synthesis” as an enduring principle (beyond streaming `tool_use`), and explicit “humans in the loop” vision language.

**Gap type:** Dilution of north-star positioning. Brief Vision is aspirational product identity; PRD stops at V1 + one near-term bullet.

**Suggested carry-forward:** Short “Beyond V1” vision paragraph in PRD §1 or §6 — brief’s 2–3 year language verbatim or tightened; tie SM-4 / FR-5 to “transparent synthesis” principle.

---

## 7. “Builders learning AgentCore” as explicit audience hook — **diluted**

**Brief carries:**
- Problem statement: gap exists “for many teams — **and for builders learning AgentCore**.”
- Secondary user: operator who deploys, demos, tears down, **extends** — framed as learning/owning the pattern.

**PRD/addendum:**
- Dev persona (UJ-2) covers deploy/demo/destroy/extend functionally.
- “Learn and own an end-to-end AgentCore + MCP pattern” appears once in Dev JTBD.
- **Not** elevated in Document Purpose, Vision, or stakes as a co-equal reason the product exists (brief implies dual audience from the problem paragraph).

**Gap type:** Minor dilution of positioning — builder-as-learner is present but buried; brief treats it as part of the *problem gap*, not only a secondary persona detail.

**Suggested carry-forward:** One sentence in PRD §0 or §1: “Serves scientists doing desk research and builders learning AgentCore via a forkable reference slice.”

---

## 8. Minor: competitive comp naming — **diluted (low materiality)**

**Brief:** Named comps include **Biomni/Phylo**, BenchSci, FutureHouse, Open Targets.  
**Addendum §E:** Biomni (Phylo dropped), BenchSci, FutureHouse, Open Targets.

**Gap type:** Trivial naming omission unless Phylo is intentionally excluded.

---

## Summary table

| # | Brief idea | PRD/addendum status | Severity |
| --- | --- | --- | --- |
| 1 | Rich problem narrative (fragmentation, hours, lock-in, anti-theater) | Missing | High (qualitative) |
| 2 | Pathway context as demo/synthesis pillar | Diluted | Medium |
| 3 | 3–5 gateway tools (min 3) | Contradicted (exactly 3) | Medium (scope) |
| 4 | “Governed / productized / discovery desk research” positioning | Diluted | Medium (qualitative) |
| 5 | Connected multi-domain demo narrative arc | Diluted | Medium (qualitative) |
| 6 | 2–3 yr composable pattern, transparent synthesis, humans in loop | Diluted | Low–medium |
| 7 | Builders learning AgentCore as problem-gap audience | Diluted | Low |
| 8 | Phylo in comp set | Diluted | Low |

---

## Reconciliation verdict

**Material gaps exist.** Core V1 mechanics align well; the largest losses are **qualitative** — problem voice, positioning phrases, pathway as a named demo beat, and the brief’s connected demo narrative. One **scope contradiction** (3–5 vs exactly 3 tools) should be explicitly resolved or logged before PRD finalize.
