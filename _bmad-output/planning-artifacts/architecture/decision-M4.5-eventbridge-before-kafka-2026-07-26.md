# Decision — M4.5 / M4.6 EventBridge before Kafka

**Status:** ADOPTED · **Date:** 2026-07-26

## Decision

1. Keep the **chat hot path** as Browser → SigV4 Stream → AgentCore Runtime (SSE).
2. If async integration is needed later, use **Amazon EventBridge** first.
3. **Do not** introduce MSK/Kafka until EventBridge is proven insufficient (throughput, fan-out, ordering) with a written decision.

## Why

- V1/V1.5 workloads are request/response research turns, not high-volume event streams.
- Kafka adds always-on cost that fights destroy-when-idle.
- EventBridge covers deploy notifications and future ingest triggers cheaply.

## Consequence

- Story **M4.6** remains **cancelled** until superseded.
- Story **M4.5** is satisfied by this decision + docs; EventBridge rules can be added when a concrete use case lands.
