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

## Repository layout

```text
.
├── agents/                 # Agent implementations (Python / Strands / AgentCore)
│   ├── unified-research-agent/
│   └── framework/
├── gateways/               # MCP / database gateway tools
│   └── database/
├── infra/                  # AWS CDK stacks and constructs
│   ├── backend/            # Auth, stream, agent, gateway, APIs
│   └── frontend/           # UI hosting and deployment
├── web/                    # React application
├── docs/                   # Design notes and guides
└── README.md
```

> Folder names may evolve as the project grows; keep this section updated.

## Prerequisites

- AWS account with Amazon Bedrock model access enabled
- AWS CLI configured with credentials
- Node.js 22+
- Python 3.12+
- Docker (agent image builds)
- AWS CDK bootstrap in the target account/region
- Optional: USPTO API key for patent search

## Configuration

Create a `.env` at the repo root when patent search is required:

```bash
USPTO_API_KEY=your_uspto_api_key_here
```

Obtain a key from the [USPTO Developer Portal](https://developer.uspto.gov/) if needed. Other tools work without it.

## Installation

```bash
git clone https://github.com/<your-org>/Drug-Discovery-Agentic-Target-Identification.git
cd Drug-Discovery-Agentic-Target-Identification

npm install
# Python deps are installed per-agent / per-gateway as documented in those folders
```

Configure your AWS account and region in CDK context (e.g. `cdk.json`), then bootstrap once:

```bash
npx cdk bootstrap aws://<ACCOUNT_ID>/<REGION>
```

## Deployment

Deploy with CDK (exact stack names depend on your infra layout):

```bash
npx cdk deploy --all
```

After deploy, open the CloudFront / frontend callback URL from stack outputs, create a Cognito user, and sign in.

To tear down:

```bash
npx cdk destroy --all
```

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

