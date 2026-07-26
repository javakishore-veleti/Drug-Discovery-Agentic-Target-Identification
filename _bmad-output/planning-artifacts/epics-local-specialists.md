# Epic L: Local specialist agent suite

**Status:** draft (Fast-path) · **Date:** 2026-07-26  
**Binds:** PRD addendum §K · `agents/README.md`  
**Production unchanged:** Epics 1–6 / `unified-research-agent` remain the only cloud path.

## Goal

Specify and harden **local-only** specialist CLIs so domain behavior is testable and prompts do not drift—without multi-agent Runtime or new CDK stacks.

## Non-goals

- Separate AgentCore Runtimes per specialist
- Supervisor as a deployed multi-agent product
- New Gateway tools beyond pubmed / clinicaltrials / chembl
- UI changes for specialist routing

---

## Story L.1: Shared framework contract

As a builder, I want specialists to share config, research-assist boundary, and V1 tools via `agents/framework/`, so that local agents stay consistent with production tool contracts.

**ACs:**

- Given `agents/framework/` · When any specialist creates an agent · Then it uses the same three tools and research-assist boundary helper  
- And no specialist package vendors a private PubMed/CT/ChEMBL client  
- And docs state framework is local helpers only (not a deploy framework)

---

## Story L.2: Drug profile analysis agent (local)

As a scientist, I want a local drug-profile CLI for MoA / toxicity / PK context, so that I can exercise that domain without the UI.

**ACs:** LA-FR-1 · package + prompt + README · example MoA query returns research-assist answer · tools from V1 set · no Runtime deploy artifacts required

---

## Story L.3: Patient risk assessment agent (local)

As a scientist, I want a local patient-risk CLI for population / vulnerability framing, so that cardiotoxicity-style questions can be tested in isolation.

**ACs:** LA-FR-2 · package + prompt + README · follow-up-style risk query works locally · refuses actionable clinical orders · V1 tools only

---

## Story L.4: Pathway mapping agent (local)

As a scientist, I want a local pathway CLI that uses literature within V1 tool limits, so that pathway questions are honest about missing pathway DBs.

**ACs:** LA-FR-3 · package + prompt + README · pathway query runs · answer or prompt acknowledges V1 tool limit when network DBs unavailable · V1 tools only

---

## Story L.5: Cardioprotection target agent (local)

As a scientist, I want a local cardiac-safety CLI, so that cardioprotection / cardiotoxicity research framing can be tested alone.

**ACs:** LA-FR-4 · package + prompt + README · cardiac safety query works · research-assist boundary held · V1 tools only

---

## Story L.6: Drug design hypothesis agent (local)

As a scientist, I want a local design-hypothesis CLI, so that safer-targeting / chemistry ideas can be tested with chembl + literature.

**ACs:** LA-FR-5 · package + prompt + README · design hypothesis query works · no invented docking/PDB claims · V1 tools only

---

## Story L.7: Medical supervisor local stubs

As a builder, I want a local supervisor stub that can route in-process to specialists, so that multi-agent patterns can be explored without cloud orchestration.

**ACs:** LA-FR-6 · package + README state NOT for Runtime · in-process stubs or documented no-op · no CDK / multi-Runtime

---

## Story L.8: Genetic risk assessment (local)

As a scientist, I want a local genetics research CLI using V1 tools only, so that ERBB2/literature genetics framing can be explored without Ensembl/GWAS Gateway.

**ACs:** LA-FR-7 · package + prompt + README · genetics literature query works · no personal counseling · V1 tools only

---

## Story L.9: Unified prompt domain consolidation (code already started)

As a builder, I want the production Unified Research Agent prompt to name the five domains, so that cloud answers stay aligned with specialist intent without deploying specialists.

**ACs:** Production prompt documents five domains · still single Runtime agent · no change to CDK/Gateway required for this story

---

## Suggested order

L.1 (done in scaffold) → L.2–L.6 harden prompts/smokes → L.7–L.8 stubs → L.9 keep unified in sync.

**Next BMAD (when investing further):** optional architecture AD update; do **not** open multi-Runtime epic until product decides to leave single-agent V1.
