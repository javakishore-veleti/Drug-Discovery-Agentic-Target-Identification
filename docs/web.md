# Research chat UI (`web/`) — Epic 5

Thin Vite + React chat for UJ-1: Cognito sign-in → Disclaimer + SigV4 Stream → tool/answer transcript → follow-up → sign-out.

**Browser path (AD-1):** User Pool → Identity Pool → temporary credentials → SigV4 → `StreamUrl`. Never AgentCore Runtime IAM in the browser.

## Configure from CDK Outputs

| Env var | Stack output |
| --- | --- |
| `VITE_USER_POOL_ID` | Auth `UserPoolId` |
| `VITE_USER_POOL_CLIENT_ID` | Auth `UserPoolClientId` |
| `VITE_IDENTITY_POOL_ID` | Auth `IdentityPoolId` |
| `VITE_STREAM_URL` | Stream `StreamUrl` |
| `VITE_AWS_REGION` | usually `us-east-1` |

```bash
cd web
cp .env.example .env.local
# fill from:
aws cloudformation describe-stacks --stack-name AgenticTargetIdAuth --query 'Stacks[0].Outputs'
aws cloudformation describe-stacks --stack-name AgenticTargetIdStream --query 'Stacks[0].Outputs[?OutputKey==`StreamUrl`]'
```

## Admin create-user (no self-signup)

See [auth.md](./auth.md). Quick path:

```bash
export USER_POOL_ID=...   # Auth UserPoolId
export SMOKE_USER_EMAIL=asha.demo@example.com
export SMOKE_USER_PASSWORD='ChangeMe-Demo12'
export AWS_REGION=us-east-1
python3 stream/scripts/create_cognito_user.py
```

## Run locally

```bash
cd web
npm install
npm run dev
```

Open the printed localhost URL → sign in → chat. Demo buttons cover Herceptin mechanism → cardiotoxicity (follow-up without restating the drug name).

## Soft stall

Client aborts after **5 minutes** with a terminal error if the Stream turn never completes (NFR-9 / Story 5.4).

## Smokes

```bash
# Same Cognito IdP → SigV4 path as the UI (no browser)
cd web && npm run e2e:herceptin

# Headless UJ-1 (requires npm run dev + playwright chromium)
cd web && npx playwright install chromium
WEB_URL=http://127.0.0.1:5173 npm run e2e:browser
```

## Out of scope (Epic 6)

S3 + CloudFront hosting / FrontendUrl.
