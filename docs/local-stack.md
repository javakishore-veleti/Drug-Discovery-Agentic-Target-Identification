# Local stack (cost-saving feature toggle)

Day-to-day UI + agent work **without** Cognito / Identity Pool / Stream Lambda / AgentCore Runtime / CloudFront.

**Split:** application processes run on the **host**; Docker is only for **dependency software** (none required for V1 yet).

You still need **AWS credentials + Bedrock model access** on the host that runs local Stream.

Local Stream **forces** `USE_GATEWAY_TOOLS=false` so tools hit public APIs (PubMed / CT.gov / ChEMBL / Open Targets) via in-process adapters — not a destroyed AgentCore Gateway URL left in `agents/unified-research-agent/.env`.

## What runs where

| Piece | Where | How |
| --- | --- | --- |
| Dependency software (Redis, etc.) | Docker only | `npm run local:deps:start` → `docker-compose.local.yml` |
| Python venv + `requirements.txt` | Host (`uv`) | `npm run local:up` / `local:env` |
| Stream (`local/stream_app.py`) | **Host** | `npm run local:up` / `local:stream` |
| Web (Vite) | **Host** | `npm run local:web` |
| Specialist agents (optional) | **Host** (local UI only) | Agent dropdown → POST `agentId` → `local/agent_registry.py` |
| Bedrock + public research APIs | Cloud / internet | Host AWS creds |

Local UI can switch among `unified` and specialist packages under `agents/` (same V1 tools, different system prompts). AWS / CloudFront path stays **unified only**.

Do **not** put the Stream or Vite UI in Docker.

### Python env (`uv`)

`local:up` always creates/syncs:

`~/runtime_data/python_venvs/drug-discovery-agentic-td`

from `agents/unified-research-agent/requirements.txt` via **uv** (no manual `pip install` step). If requirements change, Stream is restarted so new libraries load. Override with `LOCAL_PYTHON_VENV` / `LOCAL_PYTHON_VERSION` (default `3.12`).

## Toggle

| Mode | `VITE_STACK_MODE` | Auth | Stream |
| --- | --- | --- | --- |
| **local** | `local` | Demo email in `localStorage` (not Cognito) | Plain HTTP → host `:8787` |
| **aws** | `aws` (default) | Cognito → Identity Pool → SigV4 | Stream Function URL |

## Equivalents

| AWS piece | Local equivalent |
| --- | --- |
| Cognito + Identity Pool | `LocalLoginForm` (demo gate only) |
| Stream Lambda + SigV4 | Host `local/stream_app.py` (FastAPI SSE) |
| AgentCore Runtime | In-process `create_agent()` inside host Stream |
| Gateway tools | Local PubMed/CT/ChEMBL adapters (`USE_GATEWAY_TOOLS=false`) |
| CloudFront web | Host `npm run local:web` |

## Quick start (host app)

Requires [uv](https://docs.astral.sh/uv/) on your PATH.

```bash
# One pair: Stream (:8787) + Vite UI (:5173) in the background
npm run local:stream-and-ui-up
# …work…
npm run local:stream-and-ui-down
```

Open http://127.0.0.1:5173 → Continue locally → chat.

Or separately:

```bash
npm run local:up            # Stream only
npm run local:web           # UI only (foreground)
npm run local:down          # stop Stream only
```

## Adding a Docker dependency later

Edit `docker-compose.local.yml` and add a service (see commented Redis example). Keep Stream/Web on the host; point host env vars at `localhost:<port>`.

## What you are NOT paying for in local mode

- Cognito MAU / Identity Pool
- Lambda Stream + Function URL
- AgentCore Runtime + Memory
- CloudFront / S3 frontend hosting
- Gateway Lambdas (unless you set `AGENTCORE_GATEWAY_URL`)

## Production / demo path

Unset local mode and deploy CDK (`docs/deploy.md`): Cognito → Stream → Runtime → Gateway → CloudFront.
