# CDK app — Backend + Frontend (Epic 6)

Single TypeScript CDK app for the V1 pilot. Prefer consolidating here rather than parallel apps.

**Full lifecycle docs:** [`docs/deploy.md`](../../docs/deploy.md)

## Stacks

| Stack | Layer | Purpose |
| --- | --- | --- |
| `AgenticTargetIdGateway` | Backend | AgentCore Gateway + pubmed / clinicaltrials / chembl (7-day tool logs) |
| `AgenticTargetIdRuntime` | Backend | AgentCore Runtime (ARM64) + Memory STM |
| `AgenticTargetIdStream` | Backend | Stream Lambda SSE + IAM Function URL + X-Ray (7-day logs) |
| `AgenticTargetIdAuth` | Backend | Cognito User Pool + Identity Pool (no self-signup) |
| `AgenticTargetIdOps` | Ops | CloudWatch dashboard + SNS alarms (M1.3–M1.4) |
| `AgenticTargetIdFrontend` | Frontend | S3 + CloudFront; injects `/config.json`; Output `FrontendUrl` |

## Deploy (us-east-1 or CDK context region)

```bash
cd infra/backend
npm install
export GATEWAY_INVOKER_ARN="$(aws sts get-caller-identity --query Arn --output text)"

# Backend only
npx cdk deploy \
  AgenticTargetIdGateway AgenticTargetIdRuntime AgenticTargetIdStream AgenticTargetIdAuth AgenticTargetIdOps \
  --require-approval never \
  -c gatewayInvokerArn="$GATEWAY_INVOKER_ARN" \
  -c opsAlertEmail="you@example.com"

# Frontend (needs Auth + Stream Outputs via stack refs)
npx cdk deploy AgenticTargetIdFrontend \
  --require-approval never \
  -c gatewayInvokerArn="$GATEWAY_INVOKER_ARN"

# Or everything
npx cdk deploy --all --require-approval never -c gatewayInvokerArn="$GATEWAY_INVOKER_ARN"
```

## Key Outputs

| Output | Stack | Use |
| --- | --- | --- |
| `UserPoolId` / `UserPoolClientId` / `IdentityPoolId` | Auth | create-user + web SigV4 |
| `StreamUrl` | Stream | SSE Function URL |
| `FrontendUrl` | Frontend | HTTPS demo URL |
| `AgentRuntimeArn` / `AgentCoreMemoryId` | Runtime | ops / Runtime smokes |
| `GatewayUrl` | Gateway | Runtime tool path |

## Destroy when not demoing

```bash
npx cdk destroy --all --force
```

Bootstrap / log retention leftovers: see [`docs/deploy.md`](../../docs/deploy.md#leftovers-expected).

## Prerequisites

- Node.js **20+**
- Docker (Lambda asset bundling; Frontend prefers local `npm` bundling)
- Bedrock access for the pinned model
- `npx cdk bootstrap` once per account/region
