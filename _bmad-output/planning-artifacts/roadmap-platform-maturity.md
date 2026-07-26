# Platform maturity roadmap (explicitly later)

**Status:** living reference · **Date:** 2026-07-26  
**Binds:** V1 PRD (FR-1–FR-21, NFRs) · Architecture spine (AD-1…AD-15)  
**Purpose:** Record enterprise / SRE / observability / scale topics that are **intentionally out of V1** so they are not forgotten—and so they do **not** get stuffed into the PRD.

V1 product success remains SM-1…SM-5 (deploy → Herceptin demo → destroy). This file is **not** a commitment to build everything below.

---

## Maturity ladder

```text
V1 (now)       → shippable research-assist pilot; baseline security; basic logs; soft latency
V1.5           → agent eval smoke + CloudWatch dashboards/alarms (operator-facing)
V2 platform    → OTel traces, richer metrics/alerts, CloudTrail ops notes, spend alarms
V2 product     → more Gateway tools; optional RAG/vector only if a real corpus need appears
V3 ops         → blue/green (or equivalent), SLOs/on-call, event backbone only if async work appears
```

---

## What V1 already covers (do not re-spec)

| Topic | V1 home |
| --- | --- |
| Auth + no browser→AgentCore | PRD FR-1, FR-8 · NFR-1/2 · AD-1 |
| Research-assist / no PHI | PRD FR-12, Disclaimer · AD-14 |
| Soft latency / no SLA | NFR-5–7 |
| Basic debug logs | NFR-10 · AD-12 (7-day retention) |
| Destroy-when-not-demoing | FR-20 · NFR-12 |
| Exactly 3 tools; no vector DB on hot path | FR-16 · architecture deferred |

---

## Deferred catalog (not V1 FRs)

### Agent quality — Evals

| Item | Why later | Suggested first slice |
| --- | --- | --- |
| Golden-prompt eval suite | SM-1 is a manual demo bar, not regression evals | Scripted Herceptin MoA + cardiotoxicity prompts; check tool_use + PMID/NCT presence + research-assist refusal probes |
| Offline / CI eval harness | Needs stable Runtime or local agent path in CI | Run against local agent or stubbed tools before full cloud |
| Human preference / rubric scoring | Product process, not platform | Optional after golden prompts exist |

**Priority note:** Among all deferred items, **evals** are the highest *product* value before Grafana/Kafka/HA.

### Observability — OpenTelemetry, metrics, alerts, dashboards

| Item | Why later | Suggested first slice |
| --- | --- | --- |
| OpenTelemetry traces | V1 has structured CloudWatch logs only | Trace Stream → Runtime → Gateway tool spans |
| Custom metrics (latency, tool error rate, tokens) | Soft demo bars suffice now | Emit metrics from Stream Lambda + tool Lambdas |
| Alarms | No on-call; destroy-when-idle | Alarm on 5xx / stall / Bedrock throttle when shared |
| Grafana / ELK | Extra ops stack for one operator | Prefer CloudWatch dashboards first |
| CloudWatch dashboards | Nice-to-have for demos | One dashboard: stream errors, duration, tool failures |
| AWS CloudTrail | Account audit, not app feature | Document “enable Trail in account”; don’t invent product FR unless compliance buyers appear |

### Deploy / release — blue/green, canary

| Item | Why later | Suggested first slice |
| --- | --- | --- |
| Blue/green or canary | V1 model is CDK deploy + destroy | Alias / traffic shift on Runtime or CloudFront when always-on |
| Progressive delivery | Single builder, no prod SLO | After multi-environment (dev/stage/prod) exists |

### Events / async — EventBridge, MSK/Kafka

| Item | Why later | Suggested first slice |
| --- | --- | --- |
| Kafka / MSK | Chat path is request/SSE, not event fan-out | Only if batch literature ingest, webhooks, or multi-consumer pipelines appear |
| EventBridge | Same | Optional for deploy notifications or async tool fan-out later |

### SRE activities

| Item | Why later | Suggested first slice |
| --- | --- | --- |
| SLOs / error budgets | PRD rejects hard SLAs / 24×7 | Define SLOs only when the service stays up for real users |
| On-call / paging | Explicit Non-Goal | After shared production tenants |
| Capacity / load testing | Soft NFR latency only | k6/artillery against Stream URL with auth once multi-user |
| Incident runbooks | Docs cover failed-demo debug lightly | Expand when always-on |

### Security (beyond V1 baseline)

| Item | Why later | Suggested first slice |
| --- | --- | --- |
| Enterprise SSO / IdP | Non-Goal (no Federate/Midway in V1) | Cognito SAML/OIDC federation |
| WAF / Shield | Non-Goal heavy WAF | CloudFront WAF managed rules when public multi-tenant |
| Threat model / pen-test | Builder demoware | Lightweight STRIDE note before external users |
| KMS CMK / secrets productization | Public APIs need no keys in V1 | Secrets Manager when USPTO/keys appear |
| Audit export for end users | NFR-11 out | Compliance-driven |

### High availability, latency, scalability

| Item | Why later | Suggested first slice |
| --- | --- | --- |
| Multi-AZ HA commitments | Managed services already multi-AZ; no product HA promise | Document RPO/RTO only for paid tier |
| Hard latency SLOs | Soft Warm Path bars only | p95 targets after measuring real traffic |
| Horizontal scale / multi-region | Single-region pilot | Multi-region only with data/residency need |
| Concurrency limits / quotas | Single demo user | Cognito + Lambda reserved concurrency when shared |

### Data / retrieval — vector DBs, RAG

| Item | Why later | Suggested first slice |
| --- | --- | --- |
| Vector DB (OpenSearch, pgvector, etc.) | V1 evidence = live public API tools, not private corpus RAG | Add only for private PDFs/internal corpora |
| Embedding pipelines | Same | After corpus ownership and refresh policy exist |
| Hybrid search | Same | After structured tools (e.g. Open Targets) land |

---

## What must not happen

- Do **not** expand V1 PRD with full SRE/observability/HA chapters.
- Do **not** treat local specialist agents (`addendum.md` §K) as requiring Kafka, vector DB, or multi-Runtime HA.
- Do **not** optimize for tool count or dashboard count (PRD counter-metrics SM-C1…C3).

When a deferred item becomes real work: open a **new epic** (and PRD addendum section if product-facing), keep architecture decisions in the spine or a short AD note, and leave this roadmap as the backlog map.

---

## Pointers

- V1 requirements: `prds/.../prd.md`
- Mechanism / deferred tools: `prds/.../addendum.md` (§H, §K)
- Architecture invariants: `architecture/.../ARCHITECTURE-SPINE.md`
- Build order: `epics.md`
- Operator lifecycle: `docs/deploy.md`
