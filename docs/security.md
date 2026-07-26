# Security & HA notes (Stories M5.1, M5.4, M5.5)

Lightweight operator/builder notes. Not a formal pen-test report.

## Threat model (M5.1) — STRIDE-style

| Category | Risk on V1 path | Mitigations today | Later |
| --- | --- | --- | --- |
| **Spoofing** | Unauthenticated Stream invoke | Cognito + Identity Pool SigV4 on Function URL (AD-1); unsigned rejected | SSO federation (M5.3) |
| **Tampering** | Client forges sessionId | Stream mints/owns sessionId; Runtime Memory keyed by session | Stronger session binding |
| **Repudiation** | “Who called Stream?” | CloudWatch logs (`sessionId`, `requestId`); optional CloudTrail (ops) | User-facing audit export (out) |
| **Info disclosure** | Logs/prompts leak secrets or PHI | No PHI in V1; no secrets in git; research-assist only; public APIs | Secrets Manager for future keys (below) |
| **Denial of service** | Bedrock/API rate limits; Lambda floods | Soft stall terminal; tool 45s budget; destroy-when-idle | WAF (M5.2), reserved concurrency |
| **Elevation** | Browser gets Runtime IAM | **Forbidden** — only Stream role invokes Runtime (AD-1 / AD-12) | Keep invariant |

**Out of scope forever for V1 product claims:** PHI/EHR, clinical decision support, clinical-grade ranking.

## Secrets Manager pattern (M5.4)

V1 tools (PubMed / ClinicalTrials / ChEMBL) need **no** long-lived API keys.

When a future tool needs a key (e.g. USPTO):

1. Create secret in **AWS Secrets Manager** (not `.env` committed).
2. Grant **only that tool Lambda** `secretsmanager:GetSecretValue` on the secret ARN.
3. Read at cold start / invoke; never log secret values.
4. Document rotate steps in the tool README.

```text
# Conceptual — do not commit real ARNs/keys
TOOL_API_SECRET_ARN=arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:name
```

## HA / multi-AZ expectations (M5.5) — honest language

| Layer | What AWS typically provides | What we promise in V1 |
| --- | --- | --- |
| Lambda / Cognito / CloudFront / AgentCore | Managed multi-AZ resilience | Best-effort demo availability |
| Soft latency (NFR-5/6) | — | Warm-path expectations, **not** SLAs |
| Destroy-when-idle | — | Default operating model |
| Multi-region / RPO/RTO | — | **Not** offered |
| Always-on SLOs | — | Only if Epic M4.3 adopted later |

Do not market this pilot as HA enterprise SaaS. Managed services fail over; **we do not publish uptime SLAs** until an always-on environment and M4 SLOs exist.

## Related

- Auth / Stream security boundary: PRD FR-8, AD-1
- Ops alarms/dashboard: [ops.md](ops.md)
- Maturity backlog: `_bmad-output/planning-artifacts/epics-platform-maturity.md` Epic M5
