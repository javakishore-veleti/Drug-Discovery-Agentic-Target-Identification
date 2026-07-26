# Ops runbook (Stories M1.3–M1.4, M2.2–M2.5)

Operator-facing observability for Agentic Target ID. **No Grafana/ELK.** No 24×7 on-call.

**Default cost model remains destroy-when-not-demoing** ([deploy.md](deploy.md)). Alarms/dashboards matter when you leave stacks up.

## Deploy ops stack (M1.3 / M1.4)

```bash
cd infra/backend
npm install
export GATEWAY_INVOKER_ARN="$(aws sts get-caller-identity --query Arn --output text)"
# Optional email for alarm SNS (confirm subscription in inbox)
npx cdk deploy AgenticTargetIdOps --require-approval never \
  -c gatewayInvokerArn="$GATEWAY_INVOKER_ARN" \
  -c opsAlertEmail="you@example.com"
```

Or include with `--all` after Backend stacks exist. Ops depends on Stream + Gateway function names.

### Outputs

| Output | Use |
| --- | --- |
| `OpsDashboardName` / `OpsDashboardUrl` | CloudWatch dashboard (Stream errors/duration, tool errors, custom TurnErrors) |
| `OpsAlertTopicArn` | SNS topic for Stream/tool error alarms |

Dashboard name: **`AgenticTargetId-Ops`**.

## Traces (M2.1)

Stream Lambda has **AWS X-Ray** tracing enabled (`Tracing: Active` in CDK). After a turn:

1. Open **X-Ray → Traces** (or CloudWatch → X-Ray traces) in the deploy region.
2. Correlate with structured logs using `sessionId` / `requestId` from Stream log lines.
3. Tool Lambdas and AgentCore Runtime may appear as downstream segments depending on SDK/service support; Stream segment is the guaranteed V1.5 slice.

Full OpenTelemetry collector/Grafana is deferred (roadmap).

## Custom metrics (M2.2)

Stream Lambda emits **Embedded Metric Format** logs to namespace `AgenticTargetId/Stream`:

| Metric | Meaning |
| --- | --- |
| `TurnDurationMs` | Wall time for one Stream turn |
| `ToolUseCount` | tool_use events in the Runtime payload |
| `ToolErrors` | tool_result status=error count |
| `TurnErrors` | 1 if Runtime invoke failed / bad request |

Maps loosely to soft NFR-5/NFR-6 (informational — still not SLAs).

## Alert → debug runbook (M2.3)

When `agentic-target-id-stream-errors` or a tool-error alarm fires:

1. **Stream logs** — Log group for `agentic-target-id-stream`. Filter `runtime_invoke_failed` / `stream_tool_error_event`. Note `sessionId`, `requestId`, `tool`.
2. **Runtime** — Confirm AgentCore Runtime is healthy; check Bedrock model access / throttling for pinned model.
3. **Gateway tools** — Log groups for `agentic-target-id-pubmed` / `clinicaltrials` / `chembl`. Look for HTTP 429, timeouts (45s), or `status: error`.
4. **Auth** — Unsigned Function URL calls return 403 (expected). Confirm Identity Pool SigV4 for UI.
5. **Stall** — Client should terminal-error within 5 minutes if no `done` (NFR-9).

No paging rotation is required for V1 / maturity M1–M2.

## CloudTrail (M2.4) — account level

Not a product FR. Enable in the AWS account used for demos:

1. CloudTrail console → Create trail (or use organization trail).
2. Apply to this account/region (`us-east-1`).
3. Management events on; data events optional/costly.

This records AWS API activity for operators. End-user audit export remains out (NFR-11).

## Spend / budget alarms (M2.5)

Primary control: **destroy stacks when not demoing**.

Secondary (recommended if stacks stay up overnight):

```bash
# Example: monthly budget with email alert (adjust amount)
aws budgets create-budget --account-id "$(aws sts get-caller-identity --query Account --output text)" \
  --budget file://<(cat <<'EOF'
{
  "BudgetName": "AgenticTargetId-Monthly",
  "BudgetLimit": {"Amount": "50", "Unit": "USD"},
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}
EOF
)
```

Or use **Cost Anomaly Detection** / Billing console budgets UI. Tag CDK stacks with `Project=AgenticTargetId` if you add tags later for cost filters.

Also watch Bedrock model invocation costs in Cost Explorer filtered by service.

## Related

- Deploy/destroy: [deploy.md](deploy.md)
- Evals: [evals.md](evals.md)
- Security / HA honesty: [security.md](security.md)
- Specs: `epics-platform-maturity.md` M1–M2
