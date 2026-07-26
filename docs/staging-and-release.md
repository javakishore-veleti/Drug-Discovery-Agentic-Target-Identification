# Staging, release, SLOs, events (Epic M4 — docs slice)

These notes satisfy the **documentation / decision** parts of M4 without requiring an always-on multi-account setup today. Implement CDK stage namespaces when you leave destroy-when-idle.

## Staging environment (M4.1)

**Intent:** A namespaced deploy distinct from personal demo destroy-loops.

Suggested conventions (when you adopt them):

| Item | Demo (today) | Staging |
| --- | --- | --- |
| Stack prefix | `AgenticTargetId*` | `AgenticTargetIdStaging*` (or `-c stage=staging` renaming) |
| Account | Personal lab | Shared non-prod account (preferred) |
| Lifecycle | Destroy when idle | Leave up for integration |
| Users | Manual Cognito create | Same; no self-signup |

**Promote path (manual for now):**

1. Merge to `main` / tag.
2. `cdk deploy --all` in staging account with staging context.
3. Run `docs/evals.md` live suite + Herceptin UI smoke.
4. Promote same commit to “prod” account only if you maintain one.

CDK rename-by-stage can be a later story; do not block demos on it.

## Blue/green / traffic shift (M4.2) — deferred procedure

Until always-on:

- **UI:** Redeploy Frontend stack (CloudFront invalidation via BucketDeployment).
- **Runtime:** New AgentCore Runtime revision / image tag; point Stream env at new ARN; keep prior revision for rollback.
- **Rollback:** Redeploy previous git tag / prior Runtime ARN.

Full alias traffic-shift automation is optional once staging exists.

## SLO draft (M4.3) — always-on only

**Do not apply these to destroy-when-idle demos.**

| SLO | Target (draft) | Notes |
| --- | --- | --- |
| Stream success rate | ≥ 99% of authenticated turns return HTTP 200 with terminal `done` or `error` | Exclude client 403 |
| Warm-path first tool_use | Soft &lt; 30s (NFR-5) | Informational until measured |
| Error budget | 1% failed turns / 28 days | Alert via Ops SNS when breached |

On-call remains optional until staffing decides otherwise.

## Load / concurrency smoke (M4.4)

```bash
# Requires deployed StreamUrl + Cognito test user env (see stream smokes)
cd stream
python3 scripts/smoke_stream_load.py --concurrency 5 --requests 10
```

Reports error count and latency samples. Not a multi-region claim.

## Events (M4.5 / M4.6)

| Decision | Status |
| --- | --- |
| Chat hot path | Remains Stream → Runtime SSE (no Kafka) |
| Async fan-out | Prefer **EventBridge** if a use case appears (deploy notify, ingest) |
| Kafka/MSK | **Cancelled** until a decision record proves EventBridge insufficient |

See `_bmad-output/planning-artifacts/architecture/decision-M4.5-eventbridge-before-kafka-2026-07-26.md`.
