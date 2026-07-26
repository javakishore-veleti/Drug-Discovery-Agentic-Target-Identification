# Architecture note — Platform maturity (post-V1)

**Status:** backlog note · **Date:** 2026-07-26  
**Binds:** `epics-platform-maturity.md` · PRD addendum §L · `roadmap-platform-maturity.md`  
**Does not change:** AD-1…AD-15 for V1 (single Unified Research Agent, 3 tools, Stream bridge, destroy-when-idle).

## Intent

Reserve architecture headroom for maturity epics **M1–M5** without rewriting the V1 spine.

## Guardrails

| Topic | Rule until an M\* story adopts otherwise |
| --- | --- |
| Hot path | Browser → Cognito → SigV4 Stream → Runtime → Gateway tools (AD-1) |
| Vector / RAG | Off hot path; requires M3.1 decision record |
| Events | Prefer EventBridge for async; Kafka/MSK only after M4.6 gate |
| Observability | CloudWatch first (M1); OTel/X-Ray in M2; Grafana/ELK not required |
| Release | Personal demos may keep destroy/redeploy; blue/green is M4 for always-on |
| SLOs | Informational until always-on; never silently convert NFR-5/6 into SLAs |

## Future AD placeholders (not adopted)

- **AD-M-Obs** — Trace/metric correlation keys (`sessionId`, `requestId`, `tool`)
- **AD-M-Eval** — Eval harness location and CI vs on-demand
- **AD-M-Release** — Stage naming + traffic shift mechanism
- **AD-M-Retrieve** — Vector engine choice (only if M3.1 adopts)

Adopt these as numbered ADs in the spine only when the corresponding epic starts.
