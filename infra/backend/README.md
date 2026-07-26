# Backend CDK — AgentCore Gateway (Stories 2.1–2.3)

Deploys AgentCore Gateway (IAM inbound auth) with Lambda MCP targets:

- **`pubmed`** → `gateways/database/pubmed/`
- **`clinicaltrials`** → `gateways/database/clinicaltrials/`
- **`chembl`** → `gateways/database/chembl/`

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
npx cdk deploy AgenticTargetIdGateway --require-approval never \
  -c gatewayInvokerArn="$GATEWAY_INVOKER_ARN"
```

Copy `GatewayUrl` into `agents/unified-research-agent/.env` as `AGENTCORE_GATEWAY_URL`.

## Outputs

| Output | Use |
| --- | --- |
| `GatewayUrl` | MCP endpoint for the agent (`AGENTCORE_GATEWAY_URL`) |
| `GatewayId` / `GatewayArn` | Ops / IAM |
| `PubmedMcpToolName` | Logical AD-3 name: `pubmed` |
| `ClinicaltrialsMcpToolName` | Logical AD-3 name: `clinicaltrials` |
| `ChemblMcpToolName` | Logical AD-3 name: `chembl` |

AgentCore Gateway may expose wire MCP names as `${target}___${tool}`. The agent normalizes to logical AD-3 names.

## Destroy

```bash
npx cdk destroy AgenticTargetIdGateway --force
```
