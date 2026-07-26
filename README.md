# Drug-Discovery-Agentic-Target-Identification
Agentic drug-discovery platform for target identification. Researchers chat with a Bedrock AgentCore agent that uses biomedical MCP tools (PubMed, ChEMBL, ClinicalTrials, and more) to analyze mechanisms, safety, pathways, and design hypotheses for pharmaceutical R&amp;D.

## What is target identification?

**Target identification** is a core early-stage **drug discovery** concept.

In pharmaceutical R&D, a **target** is usually a biological molecule (often a protein, gene, or pathway node) believed to be causally linked to a disease and modulable by a drug. Target identification is the work of finding and justifying that target before heavy investment in chemistry and clinical development.

Typical questions include:

- What drives the disease biology?
- Is this protein or pathway druggable?
- What happens if we inhibit or activate it (efficacy and safety)?
- Which patients benefit most?
- Are there patents, prior art, or competing approaches?

It sits early in the pipeline:

**Disease biology → Target identification → Target validation → Hit/lead discovery → Optimization → Preclinical → Clinical**

## About this platform

This project is an AI-powered drug discovery platform that helps pharmaceutical R&D teams accelerate target identification, risk assessment, and drug design hypothesis generation through intelligent analysis of biomedical literature and databases.

Researchers interact through a secure chat interface. A unified research agent on **AWS Bedrock AgentCore** selects and calls specialized biomedical tools (via an MCP-style gateway) to synthesize evidence across mechanisms, patient risk, pathways, safety, and design options.

## Problem

Target identification accounts for a large share of cost and failure risk in drug development. Critical evidence is scattered across literature, clinical registries, chemistry databases, protein networks, and safety sources. This platform unifies that work into an agentic research workflow so scientists can ask multi-domain questions and get evidence-backed answers faster.

## Architecture

```text
Researcher
  → React UI (CloudFront + S3)
  → Amazon Cognito (auth)
  → Stream Lambda (SSE / SigV4)
  → Bedrock AgentCore Runtime (Unified Research Agent)
       → Foundation model (Claude on Amazon Bedrock)
       → AgentCore Memory (session context)
       → AgentCore Gateway (MCP tools)
            → Biomedical APIs (PubMed, ChEMBL, ClinicalTrials, …)
```

### Core components

| Layer | Technology | Role |
|-------|------------|------|
| Frontend | React + TypeScript | Research chat UI |
| Auth | Amazon Cognito | User authentication |
| Stream API | AWS Lambda (Function URL) | Secure streaming bridge to the agent |
| Agent runtime | Bedrock AgentCore + Strands SDK | Reasoning, tool selection, synthesis |
| Model | Claude on Amazon Bedrock | LLM inference |
| Tools | AgentCore Gateway + Lambda | Biomedical database / API access |
| Memory | AgentCore Memory / DynamoDB | Conversation and session state |
| Infra | AWS CDK | Infrastructure as code |

### Agent

**Unified Research Agent** — a single multi-domain agent covering:

- Drug profile analysis (mechanism, toxicity, PK)
- Patient risk assessment (populations, biomarkers)
- Molecular pathway mapping (interactions, networks)
- Target safety / cardioprotection analysis
- Drug design hypothesis generation
- Patent and literature intelligence (where configured)

## Key features

- Intelligent drug profiling and toxicity analysis
- Patient risk stratification and biomarker exploration
- Molecular pathway and protein-interaction intelligence
- Target safety assessment
- AI-assisted design hypothesis generation
- Streaming chat UI with tool-use visibility
- Persistent research sessions
- Biomedical tool access via gateway, including:
  - **Literature & clinical:** PubMed, ClinicalTrials.gov, OpenFDA
  - **Drug discovery:** ChEMBL, PubChem, and related sources
  - **Proteins & genomics:** UniProt, STRING, Ensembl, GTEx, GEO
  - **Pathways:** Reactome, KEGG
  - **Structural biology:** PDB, AlphaFold
  - **Patents:** USPTO (optional API key)

## Scope (V1 pilot)

Research assistance over **public** APIs (PubMed, ClinicalTrials.gov, ChEMBL) via a single AgentCore agent. **Not** clinical-grade decision support, **not** a proprietary knowledge graph, and **not** a validated-target ranking product. UI Disclaimer + agent prompt enforce research-only boundaries.

**Operating model:** deploy for demos; **destroy-when-not-demoing** to control idle cost (see [docs/deploy.md](docs/deploy.md)).

## Specs & BMAD artifacts (important)

This repo uses **[BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD)** for spec-driven development (not Kiro). Specs are **not** only under `implementation-artifacts/` — BMAD splits **planning** vs **implementation**.

| Folder | Role | Open these first |
|--------|------|------------------|
| [`_bmad-output/planning-artifacts/`](_bmad-output/planning-artifacts/) | **What & how** — requirements + design + epic breakdown | `prds/.../prd.md`, `architecture/.../ARCHITECTURE-SPINE.md`, `epics.md` |
| [`_bmad-output/implementation-artifacts/`](_bmad-output/implementation-artifacts/) | **Build execution** — sprint board + per-story completion | `sprint-status.yaml`, `stories/*.md` |

**V1 vs later platform work:** Evals, OpenTelemetry, Grafana/ELK, CloudTrail productization, blue/green, Kafka, SRE/SLOs, HA SLAs, and vector DBs are **intentionally out of V1**. See:

- Ladder / rationale: [`roadmap-platform-maturity.md`](_bmad-output/planning-artifacts/roadmap-platform-maturity.md)
- BMAD epics + ACs: [`epics-platform-maturity.md`](_bmad-output/planning-artifacts/epics-platform-maturity.md) (Epics **M1–M5**, stories `M1.1`…`M5.5`, status **backlog**)
- Lightweight FRs: PRD [`addendum.md`](_bmad-output/planning-artifacts/prds/prd-Drug-Discovery-Agentic-Target-Identification-2026-07-25/addendum.md) §L (PM-FR-1…22)

Do not expect those chapters inside the V1 PRD body.

**Started:** Golden evals (M1.1 / M1.2) — see [`docs/evals.md`](docs/evals.md).

### If you know Kiro’s `.kiro/specs/<feature>/` layout

Kiro packs requirements + design + tasks in one feature folder. BMAD spreads the same ideas across two folders:

| Kiro file | BMAD equivalent in this repo |
|-----------|------------------------------|
| `requirements.md` | `planning-artifacts/briefs/.../brief.md` + `planning-artifacts/prds/.../prd.md` (+ `addendum.md`) |
| `design.md` | `planning-artifacts/architecture/.../ARCHITECTURE-SPINE.md` (AD-1…AD-15) |
| `tasks.md` | `planning-artifacts/epics.md` → then `implementation-artifacts/stories/*.md` |

**Do not expect requirements/design inside `implementation-artifacts/`.** That folder is stories + sprint status by design. Full product intent and architecture live in `planning-artifacts/`.

Local specialist agents (non-production) are covered in `planning-artifacts/epics-local-specialists.md` and PRD addendum §K. Production cloud path remains the single **Unified Research Agent**.

## Repository layout

```text
.
├── _bmad-output/
│   ├── planning-artifacts/          # Brief, PRD, architecture, epics (requirements + design)
│   └── implementation-artifacts/    # Sprint status + story completion records
├── agents/unified-research-agent/   # Strands agent + Runtime image (production path)
├── agents/                          # Local specialist scaffolds (Epic L; not separate Runtimes)
├── gateways/database/               # pubmed / clinicaltrials / chembl Lambdas
├── infra/backend/                   # CDK: Gateway, Runtime, Stream, Auth, Frontend
├── stream/                          # Stream Lambda + smokes
├── web/                             # Vite React chat UI
├── docs/deploy.md                   # Pilot deploy / Outputs / destroy
└── README.md
```

## Prerequisites

- AWS account with Amazon Bedrock model access for the pinned model
- AWS CLI configured with credentials
- Node.js 20+, Python 3.12+, Docker (Runtime / Lambda bundling)
- CDK bootstrap once: `cd infra/backend && npx cdk bootstrap`

## Deployment (pilot)

Full steps, Outputs, create-user, Herceptin smoke, and teardown leftovers: **[docs/deploy.md](docs/deploy.md)**.

```bash
cd infra/backend
npm install
export GATEWAY_INVOKER_ARN="$(aws sts get-caller-identity --query Arn --output text)"
npx cdk deploy --all --require-approval never -c gatewayInvokerArn="$GATEWAY_INVOKER_ARN"
```

Open stack Output `FrontendUrl` (HTTPS). Create a Cognito user (`docs/auth.md`), sign in, ask the Herceptin mechanism question, confirm `tool_use` + answer.

When idle:

```bash
cd infra/backend
npx cdk destroy --all --force
```

CDK bootstrap / log retention leftovers are called out in `docs/deploy.md`.

## Example queries

- What is the mechanism of action of Herceptin?
- Which patient populations are most vulnerable to Herceptin cardiotoxicity?
- What proteins interact with HER2 in cardiac tissue?
- Search for patents related to HER2-targeted antibody therapies
- How could Herceptin be modified to reduce cardiac binding?
- Analyze Herceptin’s cardiotoxicity risk and suggest safer targeting strategies

## Security notes

- Do not commit `.env`, API keys, or AWS credentials
- Prefer least-privilege IAM for agent and gateway roles
- Use Cognito (or your IdP) for user access; do not expose AgentCore invoke from the browser without a signed backend path

## License

Apache License 2.0 (or your chosen license — update this section).

## Acknowledgments

Biomedical tool patterns draw on public scientific APIs and community projects such as [Stanford Biomni](https://github.com/snap-stanford/Biomni) database tooling concepts, adapted for an AgentCore gateway architecture.

