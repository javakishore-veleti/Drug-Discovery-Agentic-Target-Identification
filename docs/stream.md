# Stream Lambda — SSE bridge (Story 4.1)

Authenticated clients open the **Stream Function URL** and receive AD-4 Stream Events.
The Stream Lambda invokes AgentCore Runtime; **browsers and sample clients never call Runtime and never use Runtime IAM** (AD-1 / FR8).

## Event contract (AD-4)

SSE `data:` lines are JSON objects with a stable `type`:

| Type | When |
| --- | --- |
| `session_started` | First event; includes Stream-owned `sessionId` (AD-7) |
| `reasoning` | Only if Runtime exposes thinking — **never fabricated** (AD-5); often omitted in V1 |
| `token` | Answer text chunks (`text`) |
| `tool_use` / `tool_result` | Story 4.3 when tool activity is mapped |
| `error` | Turn/runtime failure (`message`, optional `code`) |
| `done` | **Only after** the Runtime turn finishes or hard-aborts |

## Deploy

Requires Gateway + Runtime (Epic 2–3) already deployable from `infra/backend`.

```bash
cd infra/backend
npm install
export CDK_DEFAULT_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
export CDK_DEFAULT_REGION=us-east-1
export GATEWAY_INVOKER_ARN=$(aws sts get-caller-identity --query Arn --output text)

npx cdk deploy AgenticTargetIdGateway AgenticTargetIdRuntime AgenticTargetIdStream \
  --require-approval never \
  -c gatewayInvokerArn="$GATEWAY_INVOKER_ARN"
```

Outputs:

| Output | Use |
| --- | --- |
| `StreamUrl` | SigV4 POST target for SSE (`STREAM_URL`) |
| `AgentRuntimeArn` | Used **only** by Stream Lambda env — not by browsers |

## Smoke (SigV4 test client)

Uses your CLI/env AWS credentials to sign the Function URL. This is **not** Cognito Identity Pool (Story 4.2) and **not** Runtime IAM.

```bash
export STREAM_URL=https://xxxx.lambda-url.us-east-1.on.aws/
export AWS_REGION=us-east-1
python3 stream/scripts/smoke_stream_sigv4.py "Reply with exactly one word: ok"
```

Expect event order roughly: `session_started` → `token`+ → `done`, with `sessionId` on `session_started`.

Multi-turn (same Chat Session):

```bash
export SESSION_ID="$(python3 - <<'PY'
import json,os,subprocess,sys
# or copy sessionId from first smoke JSON
print(os.environ.get("SESSION_ID",""))
PY
)"
# After first call prints sessionId:
export SESSION_ID=<sessionId from session_started>
python3 stream/scripts/smoke_stream_sigv4.py "What is our research focus?"
```

## Security notes

- **Do** SigV4 the `StreamUrl` via Cognito Identity Pool credentials (Story 4.2) — see [`docs/auth.md`](auth.md).
- **Do not** embed AgentCore Runtime ARNs or Runtime IAM keys in frontend code or public docs as a client path.
- Function URL auth type: `AWS_IAM` (JWT authorizer on the URL is out of V1 scope).

## Implementation notes

- Handler: `stream/handler.py` (Python 3.12).
- CDK: `infra/backend/stacks/stream-stack.ts`.
- V1 returns a buffered `text/event-stream` body after Runtime completes (Python managed runtime has no native `streamifyResponse`). Event order still satisfies AD-4; mid-turn `tool_use` / token streaming can tighten in Story 4.3 if needed.

## Tool events + failures (Story 4.3)

Runtime returns real `tool_events` from Strands message history. Stream maps them to SSE:

1. `tool_use` (tool name + optional input summary)
2. `tool_result` (`tool`, `status`, `ids`)
3. if `status: error` → `error` Stream Event (AD-8), then continue / `done`

`reasoning` is emitted **only** when Runtime exposes reasoningContent — never fabricated from answer tokens (AD-5).

Forced failure (smoke):

```bash
# body field forceToolError=pubmed|clinicaltrials|chembl
python3 stream/scripts/smoke_stream_tools_and_stall.py
```

## Observability + stall (Story 4.4)

- Stream CloudWatch log group retention: **7 days**
- Structured JSON logs include `sessionId`, `requestId`, and `tool` when applicable
- Soft stall: clients/smoke use a **300s** request timeout; Lambda timeout is 5 minutes — no terminal event → client treats as terminal error/timeout

## Browser CORS note (Epic 5)

Function URL CORS is configured in CDK. The Stream Lambda handler must **not** also emit `Access-Control-Allow-Origin` (browsers reject duplicate values).

## Epic 4 complete → Epic 5 UI

Auth (Identity Pool SigV4) + Stream SSE + tool mapping + observability. Chat UI: [web.md](./web.md).
