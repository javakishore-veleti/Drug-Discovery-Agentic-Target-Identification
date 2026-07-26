# Pilot deploy lifecycle (Epic 6)

TypeScript CDK app under `infra/backend/` deploys the V1 slice: **Backend** (Gateway + Runtime/Memory + Stream + Auth) and **Frontend** (S3 + CloudFront).

**Scope (honest):** research-assist chat over public biomedical APIs (PubMed, ClinicalTrials.gov, ChEMBL). **Not** clinical-grade decision support, **not** a proprietary knowledge graph, **not** a validated-target ranking platform. See PRD Disclaimer / addendum §F.

**Cost habit:** destroy-when-not-demoing (Story 6.4 / NFR12). Leave stacks up only while actively demoing.

## Prerequisites

- Node.js 20+, Docker (Lambda / optional web bundling), AWS CLI credentials
- Bedrock model access for the pinned model (`us.anthropic.claude-sonnet-4-6` or context override)
- One-time bootstrap per account/region: `cd infra/backend && npx cdk bootstrap`

## Backend stacks (Story 6.1)

| Stack | Role | 7-day logs |
| --- | --- | --- |
| `AgenticTargetIdGateway` | AgentCore Gateway + 3 tool Lambdas | tool log groups |
| `AgenticTargetIdRuntime` | Runtime container + Memory STM | Memory expiry 7d; Runtime service logs |
| `AgenticTargetIdStream` | SSE Stream Lambda + IAM Function URL | Stream log group |
| `AgenticTargetIdAuth` | Cognito User Pool + Identity Pool → Stream SigV4 | — |

**IAM (AD-12, summary):** Stream invokes Runtime + writes logs; Runtime invokes Bedrock pin + Gateway + Memory + logs; each tool Lambda reaches only its public API + logs; browsers never receive Runtime IAM (AD-1).

```bash
cd infra/backend
npm install
export GATEWAY_INVOKER_ARN="$(aws sts get-caller-identity --query Arn --output text)"
npx cdk deploy \
  AgenticTargetIdGateway AgenticTargetIdRuntime AgenticTargetIdStream AgenticTargetIdAuth \
  --require-approval never \
  -c gatewayInvokerArn="$GATEWAY_INVOKER_ARN"
```

### Required Outputs (Backend)

| Output | Stack | Use |
| --- | --- | --- |
| `UserPoolId` | Auth | admin create-user |
| `UserPoolClientId` | Auth | Cognito app client / web config |
| `IdentityPoolId` | Auth | browser SigV4 credentials |
| `StreamUrl` | Stream | SigV4 POST target (SSE) |
| `AgentRuntimeArn` | Runtime | ops / Runtime smokes (not for browsers) |
| `AgentCoreMemoryId` | Runtime | Runtime env (auto-wired) |
| `GatewayUrl` / `GatewayId` | Gateway | Runtime env / ops |

No secrets or long-lived AWS keys belong in the repo (NFR3). Use CDK Outputs + admin-set passwords locally.

## Frontend stack (Story 6.2)

| Stack | Role |
| --- | --- |
| `AgenticTargetIdFrontend` | S3 (private) + CloudFront HTTPS; injects `/config.json` from Backend Outputs |

```bash
cd infra/backend
export GATEWAY_INVOKER_ARN="$(aws sts get-caller-identity --query Arn --output text)"
npx cdk deploy AgenticTargetIdFrontend \
  --require-approval never \
  -c gatewayInvokerArn="$GATEWAY_INVOKER_ARN"
```

Or deploy **everything**: `npx cdk deploy --all --require-approval never -c gatewayInvokerArn="$GATEWAY_INVOKER_ARN"`.

| Output | Use |
| --- | --- |
| `FrontendUrl` | Open in browser (HTTPS CloudFront) |

Example after deploy: `aws cloudformation describe-stacks --stack-name AgenticTargetIdFrontend --query 'Stacks[0].Outputs'`.

`config.json` fields: `region`, `userPoolId`, `userPoolClientId`, `identityPoolId`, `streamUrl`.

Local Vite still uses `web/.env.local` (see [web.md](./web.md)).

## Create demo user (Story 6.3)

```bash
export USER_POOL_ID=...          # Auth UserPoolId
export SMOKE_USER_EMAIL=asha.demo@example.com
export SMOKE_USER_PASSWORD='ChangeMe-Demo12'
export AWS_REGION=us-east-1
python3 stream/scripts/create_cognito_user.py
```

Details: [auth.md](./auth.md).

## Herceptin smoke path (<15 min after deploy)

1. Open `FrontendUrl` (or `npm run dev` in `web/` with Outputs in `.env.local`).
2. Sign in with the admin-provisioned user.
3. Confirm Disclaimer is visible.
4. Ask: **What is the mechanism of action of Herceptin?**
5. Expect `tool_use` (e.g. pubmed) and a streamed answer with PMID(s) when tools return them.
6. Optional follow-up: **Which patient populations are most vulnerable to its cardiotoxicity?** (without restating the drug name).
7. Sign out.

CLI equivalents (ops / CI):

```bash
# Identity Pool SigV4 stream
python3 stream/scripts/smoke_stream_identity_pool.py "What is the mechanism of action of Herceptin?"

# Same path as UI without browser
cd web && npm run e2e:herceptin
```

## Destroy (Story 6.4)

**Default when idle:** destroy app stacks so you are not paying for Runtime/Gateway/CloudFront overnight.

```bash
cd infra/backend
export GATEWAY_INVOKER_ARN="$(aws sts get-caller-identity --query Arn --output text)"
# Frontend first, then Backend (dependency-friendly order)
npx cdk destroy AgenticTargetIdFrontend --force
npx cdk destroy \
  AgenticTargetIdAuth AgenticTargetIdStream AgenticTargetIdRuntime AgenticTargetIdGateway \
  --force
```

Or: `npx cdk destroy --all --force`.

### Leftovers (expected)

These are **not** removed by app `cdk destroy` and may retain small cost or data:

- **CDK bootstrap** stack (`CDKToolkit`) and bootstrap ECR/S3 assets
- **CloudWatch log groups** already created (7-day retention; may linger until empty/expired depending on account settings)
- **ECR images** pushed for Runtime asset publishing (account lifecycle rules may apply)
- **Cognito** users are deleted with the User Pool when Auth is destroyed

Re-bootstrap only if you delete `CDKToolkit` intentionally.

## Related docs

- [auth.md](./auth.md) — Cognito → Identity Pool → Stream SigV4
- [stream.md](./stream.md) — Stream events + observability
- [web.md](./web.md) — local Vite UI
- [runtime.md](./runtime.md) — Runtime packaging / Memory
- [tool-result-contract.md](./tool-result-contract.md) — tool_result shape
