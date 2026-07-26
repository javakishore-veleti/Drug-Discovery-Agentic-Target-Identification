# Backend CDK — AgentCore Gateway (Story 2.1)

Deploys AgentCore Gateway (IAM inbound auth) with a Lambda MCP target whose **tool schema name is exactly `pubmed`**, reusing `gateways/database/pubmed/adapter.py`.

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

AgentCore Gateway may expose the wire MCP name as `pubmed___pubmed` (target___tool). The agent normalizes to logical `pubmed`.

## Destroy

```bash
npx cdk destroy AgenticTargetIdGateway --force
```
