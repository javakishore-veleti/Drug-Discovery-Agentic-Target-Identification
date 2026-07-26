# Agentic Target ID

**Agentic AI** research-assist pilot for early **drug-discovery target identification**, built with **BMAD Method** specs and **AWS Bedrock AgentCore**.

Scientists chat in natural language. A single **Unified Research Agent** plans tool use, streams live `tool_use` / answer events, and cites public source IDs (PMID / NCT / ChEMBL; optional Ensembl via Open Targets)—without the browser ever calling AgentCore directly.

> Research assistance only. **Not** medical advice, clinical decision support, or a validated-target ranking product.

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

## Problem

Target identification accounts for a large share of cost and failure risk in drug development. Critical evidence is scattered across literature, clinical registries, chemistry databases, protein networks, and safety sources. This platform unifies that work into an **agentic** research workflow so scientists can ask multi-domain questions and get evidence-backed answers faster—via **AWS Bedrock AgentCore**, governed Gateway tools, and live Stream Events.

## Why agentic (not a chatbot wrapper)

| Capability | What you get |
| --- | --- |
| **Plan → act → synthesize** | Agent selects biomedical tools, reads results, answers with citations |
| **Visible tool use** | SSE Stream Events show which Gateway tools ran |
| **Governed tools** | MCP-style AgentCore Gateway; shared timeout / 429 / `status: error` contract |
| **Multi-turn memory** | Same Chat Session follow-ups keep Herceptin/HER2 context |
| **Secure cloud path** | Cognito → Identity Pool → **SigV4** Stream Lambda → Runtime (AD-1) |
| **Spec-driven** | BMAD planning + implementation artifacts (not Kiro) |

## Cloud architecture (AWS)

```text
Scientist (browser)
  → React UI (CloudFront + S3) + Cognito
  → Stream Lambda (SSE / SigV4 Function URL)
  → Bedrock AgentCore Runtime  ← Claude on Amazon Bedrock
       ├─ AgentCore Memory (in-session)
       └─ AgentCore Gateway (MCP tools)
            → PubMed · ClinicalTrials.gov · ChEMBL
            → optional Open Targets (-c enableTool4=true)
```

**Building blocks:** Bedrock + AgentCore Runtime/Gateway/Memory · Lambda Stream bridge · Cognito · CDK · CloudWatch ops (dashboard/alarms/X-Ray/EMF when Ops stack is deployed).

## Stream Events (live functionality)

The Stream Lambda emits typed SSE events the UI understands:

`session_started` → optional `reasoning` → `tool_use` / `tool_result` → `token`… → `error`? → `done`

- Browser **never** invokes AgentCore Runtime IAM credentials.
- Tool failures surface as `error` / failed `tool_result`; the session stays usable.
- Soft stall: UI/client terminals if no `done` within ~5 minutes.

## What’s shipped (V1 + beyond)

**V1 core is complete** (Epics 1–6): Cognito chat UI · Stream Events (SSE / SigV4) · Unified Research Agent on AgentCore · Memory · CDK deploy/destroy · Herceptin MoA → cardiotoxicity multi-turn demo.

### Gateway tools

| Tool | Citations | Deploy |
| --- | --- | --- |
| **pubmed** | `ids.pmid` | Default (V1) |
| **clinicaltrials** | `ids.nct` | Default (V1) |
| **chembl** | `ids.chembl` | Default (V1) |
| **opentargets** | Ensembl / Open Targets evidence | **Beyond V1** — `-c enableTool4=true` (M3.3) |

Default CDK deploy still wires the **three** V1 tools so FR-16 stays cheap/simple; turn on tool #4 when you want target-evidence depth.

### Platform maturity (also beyond V1)

Shipped slices from Epics **M1–M5** (see sprint board):

- **Evals** — golden-prompt harness ([`docs/evals.md`](docs/evals.md))
- **Ops** — CloudWatch dashboard, alarms, X-Ray, EMF ([`docs/ops.md`](docs/ops.md))
- **Security** — threat model, optional CloudFront WAF (`-c enableWaf=true`), SSO spike notes ([`docs/security.md`](docs/security.md))
- **Staging / release** — staging notes, SLO drafts, EventBridge-before-Kafka ([`docs/staging-and-release.md`](docs/staging-and-release.md))
- **Epic L** — local specialist agent CLIs for domain experiments; **cloud production path stays one Unified Research Agent**

### Still out of scope (by design)

Multi-agent cloud swarm · vector RAG (blocked) · Kafka (cancelled) · enterprise SSO (docs spike only) · clinical-grade claims · USPTO / full pathway DB suite in the Gateway.

Roadmap detail: [`roadmap-platform-maturity.md`](_bmad-output/planning-artifacts/roadmap-platform-maturity.md) · [`epics-platform-maturity.md`](_bmad-output/planning-artifacts/epics-platform-maturity.md).

## BMAD Method (how this repo is specified)

This project is a **BMAD** mastery / reference build (spec-driven), not Kiro.

| Phase | Where | Role |
| --- | --- | --- |
| Planning | [`_bmad-output/planning-artifacts/`](_bmad-output/planning-artifacts/) | Brief, PRD (+ addendum), architecture spine (AD-1…AD-15), epics |
| Implementation | [`_bmad-output/implementation-artifacts/`](_bmad-output/implementation-artifacts/) | Sprint board + per-story records |

**Kiro → BMAD map:** `requirements.md` ≈ brief+PRD · `design.md` ≈ architecture spine · `tasks.md` ≈ epics → stories.

## Example research turns

- What is the mechanism of action of Herceptin?
- Which patient populations are most vulnerable to its cardiotoxicity? *(follow-up, same session)*
- Use Open Targets to find ERBB2 / HER2 target evidence and cite Ensembl ids *(deploy with `enableTool4=true`)*
- What ChEMBL context exists for trastuzumab / HER2-targeted agents?

## Deploy (pilot)

**Cost habit:** deploy for demos; **destroy-when-not-demoing**. Full lifecycle: [`docs/deploy.md`](docs/deploy.md).

```bash
cd infra/backend
npm install
export GATEWAY_INVOKER_ARN="$(aws sts get-caller-identity --query Arn --output text)"
npx cdk bootstrap   # once per account/region if CDKToolkit is absent
npx cdk deploy --all --require-approval never \
  -c gatewayInvokerArn="$GATEWAY_INVOKER_ARN"
# Optional: -c enableTool4=true  -c enableWaf=true  -c opsAlertEmail=you@example.com
```

Then: create Cognito user ([`docs/auth.md`](docs/auth.md)) → open `FrontendUrl` → Herceptin MoA → confirm live `tool_use` + streamed answer.

```bash
npx cdk destroy --all --force -c gatewayInvokerArn="$GATEWAY_INVOKER_ARN"
```

### Prerequisites

- AWS account with Bedrock model access for the pinned Claude model
- AWS CLI credentials · Node.js 20+ · Python 3.12+ · Docker (Runtime / Lambda bundling)

### Manual CI (not automatic)

GitHub **Actions → Manual checks → Run workflow** (`workflow_dispatch` only). Runs golden evals `--dry-run`, Python compileall, optional Open Targets adapter smoke—**never** on every push/PR.

## Security

- No secrets or AWS keys in git
- Cognito + SigV4 Stream only; no browser→AgentCore Runtime invoke
- Least-privilege IAM for Stream / Runtime / tool Lambdas
- Optional CloudFront WAF: `-c enableWaf=true`

## License

[MIT](LICENSE) © 2026 Kishore Veleti

## Acknowledgments

Patterns for biomedical tool access draw on public scientific APIs and community ideas such as [Stanford Biomni](https://github.com/snap-stanford/Biomni) database tooling concepts, adapted here for an AgentCore Gateway architecture.
