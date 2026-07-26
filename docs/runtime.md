# AgentCore Runtime — Unified Research Agent (Story 3.1)

Single Strands agent container for Amazon Bedrock AgentCore Runtime (AD-2, AD-6).

## Packaging

| Item | Location |
| --- | --- |
| Dockerfile (linux/arm64) | `agents/unified-research-agent/Dockerfile` |
| HTTP contract | `unified_research_agent/runtime_app.py` — `POST /invocations`, `GET /ping` on **8080** |
| CDK | `infra/backend/stacks/runtime-stack.ts` (`AgentRuntimeArtifact.fromAsset`) |
| Model pin | `BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-6` (AD-6; Sonnet 4.0 EOL in many accounts) |
| Gateway tools | `AGENTCORE_GATEWAY_URL` + `USE_GATEWAY_TOOLS=true` |

Build context is the **repository root** so the image includes `gateways/database/` adapters.

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

## Destroy when idle

```bash
cd infra/backend
npx cdk destroy AgenticTargetIdRuntime AgenticTargetIdGateway --force
```

CDK bootstrap / log retention leftovers may remain (AD-11).

## Out of scope (Story 3.2+)

- AgentCore Memory (`AGENTCORE_MEMORY_ID`)
- Stream Lambda / Cognito UI
