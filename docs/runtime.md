# AgentCore Runtime — Unified Research Agent (Stories 3.1–3.2)

Single Strands agent container for Amazon Bedrock AgentCore Runtime (AD-2, AD-6)
with in-session AgentCore Memory STM (AD-7 / Story 3.2).

## Packaging

| Item | Location |
| --- | --- |
| Dockerfile (linux/arm64) | `agents/unified-research-agent/Dockerfile` |
| HTTP contract | `unified_research_agent/runtime_app.py` — `POST /invocations`, `GET /ping` on **8080** |
| CDK | `infra/backend/stacks/runtime-stack.ts` (`AgentRuntimeArtifact.fromAsset` + `Memory`) |
| Model pin | `BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-6` (AD-6; Sonnet 4.0 EOL in many accounts) |
| Gateway tools | `AGENTCORE_GATEWAY_URL` + `USE_GATEWAY_TOOLS=true` |
| Memory STM | `AGENTCORE_MEMORY_ID` only (no `MEMORY_ID` alias) |

Build context is the **repository root** so the image includes `gateways/database/` adapters.

V1 Memory is **in-session only** — no session-list UI and no cross-day resume UI.

## Local container smoke (optional)

```bash
# from repo root
docker buildx build --platform linux/arm64 \
  -f agents/unified-research-agent/Dockerfile \
  -t agentic-target-id-ura:local --load .

docker run --rm -p 8080:8080 \
  -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_SESSION_TOKEN \
  -e AWS_REGION=us-east-1 \
  -e BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-6 \
  -e USE_GATEWAY_TOOLS=false \
  agentic-target-id-ura:local

curl -s http://localhost:8080/ping
curl -s -X POST http://localhost:8080/invocations \
  -H 'Content-Type: application/json' \
  -d '{"input":{"prompt":"Reply with exactly one word: ok"}}'
```

## Deploy (Gateway + Runtime)

```bash
cd infra/backend
npm install
export CDK_DEFAULT_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
export CDK_DEFAULT_REGION=us-east-1
export GATEWAY_INVOKER_ARN=$(aws sts get-caller-identity --query Arn --output text)

npx cdk deploy AgenticTargetIdGateway AgenticTargetIdRuntime \
  --require-approval never \
  -c gatewayInvokerArn="$GATEWAY_INVOKER_ARN"
```

Outputs include `AgentRuntimeArn`, `GatewayUrl`, `BedrockModelId`.

## Invoke Runtime smoke

```bash
cd agents/unified-research-agent
export AGENT_RUNTIME_ARN=arn:aws:bedrock-agentcore:us-east-1:ACCOUNT:runtime/RUNTIME_ID
export AWS_REGION=us-east-1
python scripts/smoke_runtime_invoke.py "Reply with exactly one word: ok"
# Optional Gateway proof:
python scripts/smoke_runtime_invoke.py \
  "Use the pubmed tool once for query: trastuzumab HER2. Reply with one PMID only."
```

Expect JSON with `"status":"success"`, pinned `model_id`, and `gateway_tools: true` when the Runtime has `AGENTCORE_GATEWAY_URL`.

With Gateway configured on the Runtime, tool calls use MCP (`pubmed` / `clinicaltrials` / `chembl`).

**IAM note:** Runtime execution role needs cross-region `bedrock:InvokeModel*` on `arn:aws:bedrock:*::foundation-model/*` so US inference profiles (e.g. `us.anthropic.claude-sonnet-4-6`) can resolve.

## Two-turn Memory smoke (Story 3.2)

Same `runtimeSessionId` for both invokes. Turn 1 sets research focus `trastuzumab`; turn 2 asks for the focus compound without restating it.

```bash
cd agents/unified-research-agent
export AGENT_RUNTIME_ARN=arn:aws:bedrock-agentcore:us-east-1:ACCOUNT:runtime/RUNTIME_ID
export AWS_REGION=us-east-1
python scripts/smoke_runtime_memory_two_turn.py
```

Expect `ok: true`, `memory: true` / `memory_id_configured: true`, and turn 2 naming trastuzumab/Herceptin.
Runtime env must include `AGENTCORE_MEMORY_ID` (CDK output `AgentCoreMemoryId`).

## Herceptin multi-turn Runtime smoke (Story 3.3 / Epic 3)

Same `runtimeSessionId`. Proves FR10 + FR17 on AgentCore with Gateway tools + Memory.

| Turn | Prompt |
| --- | --- |
| 1 | What is the mechanism of action of Herceptin? |
| 2 | Which patient populations are most vulnerable to its cardiotoxicity? |

```bash
cd agents/unified-research-agent
export AGENT_RUNTIME_ARN=arn:aws:bedrock-agentcore:us-east-1:ACCOUNT:runtime/RUNTIME_ID
export AWS_REGION=us-east-1
python scripts/smoke_runtime_herceptin_multiturn.py
```

Expect `ok: true`, turn 2 still in Herceptin/HER2 context (drug name not restated in the prompt),
research-assist boundary held, and at least one PMID/NCT/ChEMBL when tools return them.

## Destroy when idle

```bash
cd infra/backend
npx cdk destroy AgenticTargetIdRuntime AgenticTargetIdGateway --force
```

CDK bootstrap / log retention leftovers may remain (AD-11).

## Out of scope (Epic 4+)

- Stream Lambda / Cognito / React UI
