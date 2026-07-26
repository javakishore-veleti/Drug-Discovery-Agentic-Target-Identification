# Backend CDK — Gateway + Runtime (Epics 2–3)

## Stacks

| Stack | Purpose |
| --- | --- |
| `AgenticTargetIdAuth` | Cognito User Pool + Identity Pool (Story 4.2 / AD-1) |
| `AgenticTargetIdGateway` | AgentCore Gateway + pubmed / clinicaltrials / chembl Lambdas |
| `AgenticTargetIdRuntime` | AgentCore Runtime (ARM64 agent) + Memory STM (`AGENTCORE_MEMORY_ID`) |
| `AgenticTargetIdStream` | Stream Lambda SSE + IAM Function URL (Stories 4.1–4.2) |

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
npx cdk deploy AgenticTargetIdAuth AgenticTargetIdGateway AgenticTargetIdRuntime AgenticTargetIdStream \
  --require-approval never \
  -c gatewayInvokerArn="$GATEWAY_INVOKER_ARN"
```

Copy `GatewayUrl` into `agents/unified-research-agent/.env` as `AGENTCORE_GATEWAY_URL` for local agent CLI. Runtime receives the same URL via env automatically.

Stream + Cognito Identity Pool SigV4: [`docs/stream.md`](../../docs/stream.md), [`docs/auth.md`](../../docs/auth.md).

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
| `AgentCoreMemoryId` | Set as `AGENTCORE_MEMORY_ID` on Runtime (Story 3.2) |
| `StreamUrl` | IAM Function URL for SSE clients (`STREAM_URL`) — never give browsers Runtime IAM |
| `UserPoolId` / `UserPoolClientId` / `IdentityPoolId` | Cognito admin create-user + Identity Pool SigV4 (Story 4.2) |

AgentCore Gateway may expose wire MCP names as `${target}___${tool}`. The agent normalizes to logical AD-3 names.

Story **2.4**: default deploy exposes **exactly** those three tools. Shared `tool_result` contract (status / tool / ids / summary / message): [`docs/tool-result-contract.md`](../../docs/tool-result-contract.md).

## Destroy

```bash
npx cdk destroy AgenticTargetIdRuntime AgenticTargetIdGateway --force
```