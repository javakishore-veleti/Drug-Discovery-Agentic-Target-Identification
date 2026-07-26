# Cognito auth → Stream SigV4 (Story 4.2)

V1 UI→Stream path (AD-1 / AD-10):

**Cognito User Pool (email/password) → Identity Pool → temporary AWS credentials → SigV4 → IAM Function URL (`StreamUrl`).**

- No JWT authorizer on the Function URL.
- No AgentCore Runtime IAM in the browser.
- Users are **admin-provisioned** (no self-signup UI).

## Outputs

| Output | Stack | Use |
| --- | --- | --- |
| `UserPoolId` | Auth | `admin-create-user` / create script |
| `UserPoolClientId` | Auth | `InitiateAuth` client id |
| `IdentityPoolId` | Auth | `GetId` / `GetCredentialsForIdentity` |
| `StreamUrl` | Stream | SigV4 POST target |

## Deploy (in place)

```bash
cd infra/backend
export GATEWAY_INVOKER_ARN="$(aws sts get-caller-identity --query Arn --output text)"
npx cdk deploy AgenticTargetIdAuth AgenticTargetIdStream \
  --require-approval never \
  -c gatewayInvokerArn="$GATEWAY_INVOKER_ARN"
```

Gateway/Runtime can stay as-is; Auth is new and Stream is updated to grant the Identity Pool authenticated role.

## Create a demo user

```bash
export USER_POOL_ID=...          # Auth stack output
export SMOKE_USER_EMAIL=asha.demo@example.com
export SMOKE_USER_PASSWORD='ChangeMe-Demo12'
export AWS_REGION=us-east-1

python3 stream/scripts/create_cognito_user.py
```

Equivalent CLI:

```bash
aws cognito-idp admin-create-user \
  --user-pool-id "$USER_POOL_ID" \
  --username "$SMOKE_USER_EMAIL" \
  --user-attributes Name=email,Value="$SMOKE_USER_EMAIL" Name=email_verified,Value=true \
  --message-action SUPPRESS

aws cognito-idp admin-set-user-password \
  --user-pool-id "$USER_POOL_ID" \
  --username "$SMOKE_USER_EMAIL" \
  --password "$SMOKE_USER_PASSWORD" \
  --permanent
```

## Smoke: Identity Pool SigV4 (+ unsigned reject)

```bash
export STREAM_URL=https://....lambda-url.us-east-1.on.aws/
export USER_POOL_ID=...
export USER_POOL_CLIENT_ID=...
export IDENTITY_POOL_ID=...
export SMOKE_USER_EMAIL=asha.demo@example.com
export SMOKE_USER_PASSWORD='ChangeMe-Demo12'
export AWS_REGION=us-east-1

python3 stream/scripts/smoke_stream_identity_pool.py "Reply with exactly one word: ok"
```

Expect:

- `unsigned_status` ∈ {401, 403}
- `signed_status` = 200 with `session_started` → `token`* → `done`
- JSON summary `"auth": "cognito_identity_pool_sigv4"`

Ops CLI SigV4 with long-lived IAM (Story 4.1) may still work if `gatewayInvokerArn` was granted — that is for builders only, not the browser path.

## Out of scope

- React hosted UI (Epic 5)
- JWT authorizer on Function URL (Deferred)
- Tool event mapping (Story 4.3)
