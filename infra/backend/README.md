# Backend CDK — Gateway + Runtime (Epics 2–3)

## Stacks

| Stack | Purpose |
| --- | --- |
| `AgenticTargetIdGateway` | AgentCore Gateway + pubmed / clinicaltrials / chembl Lambdas |
| `AgenticTargetIdRuntime` | AgentCore Runtime (Unified Research Agent ARM64 container) |

Gateway tools:

- **`pubmed`** → `gateways/database/pubmed/`
- **`clinicaltrials`** → `gateways/database/clinicaltrials/`
- **`chembl`** → `gateways/database/chembl/`

Runtime packaging + smoke: [`docs/runtime.md`](../../docs/runtime.md).

## Prerequisites

- Node.js **20+**
- Docker (Lambda asset bundling)
- AWS credentials with rights to create Lambda, IAM roles, and Bedrock AgentCore Gateway
- Bootstrap once per account/region: `npx cdk bootstrap`

## Deploy

```bash
cd infra/backend
npm install
export GATEWAY_INVOKER_ARN="$(aws sts get-caller-identity --query Arn --output text)"
# Gateway only, or Gateway + Runtime (Story 3.1):
npx cdk deploy AgenticTargetIdGateway AgenticTargetIdRuntime --require-approval never \
  -c gatewayInvokerArn="$GATEWAY_INVOKER_ARN"
```

Copy `GatewayUrl` into `agents/unified-research-agent/.env` as `AGENTCORE_GATEWAY_URL` for local agent CLI. Runtime receives the same URL via env automatically.

## Outputs

| Output | Use |
| --- | --- |
| `GatewayUrl` | MCP endpoint for the agent (`AGENTCORE_GATEWAY_URL`) |
| `GatewayId` / `GatewayArn` | Ops / IAM |
| `PubmedMcpToolName` | Logical AD-3 name: `pubmed` |
| `ClinicaltrialsMcpToolName` | Logical AD-3 name: `clinicaltrials` |
| `ChemblMcpToolName` | Logical AD-3 name: `chembl` |
| `AgentRuntimeArn` | `InvokeAgentRuntime` / smoke (`AGENT_RUNTIME_ARN`) |
| `BedrockModelId` | Pinned AD-6 model on Runtime |

AgentCore Gateway may expose wire MCP names as `${target}___${tool}`. The agent normalizes to logical AD-3 names.

Story **2.4**: default deploy exposes **exactly** those three tools. Shared `tool_result` contract (status / tool / ids / summary / message): [`docs/tool-result-contract.md`](../../docs/tool-result-contract.md).

## Destroy

```bash
npx cdk destroy AgenticTargetIdRuntime AgenticTargetIdGateway --force
```