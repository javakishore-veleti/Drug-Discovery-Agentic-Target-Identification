# Version & Technology Reality Check

**Reviewer lens:** Verify committed Stack decisions and `[ADOPTED]` technology choices were web-researched or reality-checked—not asserted from training data.

**Spine:** `ARCHITECTURE-SPINE.md` (Agentic Target ID V1)  
**Review date:** 2026-07-25  
**Method:** Independent web checks against npm, PyPI, AWS docs, Node release schedule, and AWS blogs.

---

## Verdict

**PASS (with minor caveats).** The Stack table’s claim *“versions web-checked 2026-07-25”* is substantiated for all pinned versions and named AWS services. Assumption-tagged items (Vite, Stream Lambda language) are correctly not presented as verified pins. No blocking hallucinations found.

---

## Item-by-item checks

| Item | Spine claim | Web check result | Status |
| --- | --- | --- | --- |
| `aws-cdk-lib` ^2.262 | TypeScript IaC pin | **Exists.** v2.262.0 (2026-07-22), v2.262.1 (2026-07-24) on npm/GitHub releases. Current line at review time. | ✅ Verified |
| `strands-agents` ^1.47 | Agent SDK pin | **Exists.** v1.47.0 on PyPI (2026-07-10). Requires Python ≥3.10; compatible with 3.12. Official Strands + AgentCore integration documented. | ✅ Verified |
| Bedrock model `us.anthropic.claude-sonnet-4-20250514-v1:0` | Pinned US inference profile (AD-6) | **Valid geo inference ID** per [Claude Sonnet 4 model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-4.html). Base ID `anthropic.claude-sonnet-4-20250514-v1:0` also valid. Requires operator model-access enablement—spine documents this as `[ASSUMPTION]` with 3.7 Sonnet fallback. | ✅ Verified (access caveat noted) |
| AgentCore Runtime + Gateway + Memory | Managed services for agent, MCP tools, session memory | **Real, GA.** AgentCore is a documented AWS product (GA ~Oct 2025). Runtime, Gateway, and Memory all supported in **us-east-1** per [AgentCore regions](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-regions.html). Strands listed as supported framework. | ✅ Verified |
| CDK `aws-bedrockagentcore` in 2.262 | Stable constructs for Runtime/Gateway/Memory | **Available and stable.** Graduated from alpha in CDK 2.260+; documented at `aws-cdk-lib/aws-bedrockagentcore` for 2.262.1. Runtime, Gateway, Memory constructs present. | ✅ Verified |
| Node.js 22.x | CDK + `web/` runtime | **Supported LTS.** Node 22 is **Maintenance LTS** (EOL 2027-04-30); latest patch 22.23.2 (2026-07-22). Node 24 is Active LTS—22 is acceptable for demo/V1 but not the greenfield default Node project now recommends. | ✅ Verified (minor freshness note) |
| Python 3.12 | Agent + tool Lambdas | **Supported.** Lambda managed runtime `python3.12` (AL2023) with deprecation 2028-10-31 per AWS Lambda docs. Compatible with strands-agents (≥3.10). | ✅ Verified |
| Cognito Identity Pool + SigV4 → Function URL | Preferred UI→Stream auth (AD-1, Consistency) | **Valid documented pattern.** Function URL `AuthType: AWS_IAM` + Cognito Identity Pool temporary creds + SigV4 signing is described in AWS community/docs (e.g. DEV Community “protected Lambda function URLs”). Requires `lambda:InvokeFunctionUrl` (and often `lambda:InvokeFunction`) on authenticated IAM role; CORS preflight with session-token signing needs careful frontend setup. | ✅ Verified (implementation caveats) |

---

## Greenfield starter defaults (assumption-tagged)

These are **not** committed Stack pins; spine marks them `[ASSUMPTION]`—appropriate.

| Item | Reality check | Status |
| --- | --- | --- |
| Vite + React 18+ for `web/` | Vite remains standard greenfield React default in 2026; React 18+ current. Not pinned in Stack table. | ✅ Reasonable assumption |
| Stream Lambda = Python 3.12 | Valid Lambda runtime; aligns with agent ecosystem. Node 22 also listed as alternative in Stack. | ✅ Reasonable assumption |
| Gateway targets = Lambdas | Matches AgentCore Gateway docs (Lambda as MCP target). | ✅ Verified pattern |

---

## Top findings

1. **All pinned versions exist and fit.** `aws-cdk-lib@2.262`, `strands-agents@1.47.0`, and the Sonnet 4 US inference profile are real, current, and mutually compatible for the described architecture.

2. **AgentCore triad is production-real in us-east-1.** Runtime, Gateway, and Memory are GA, region-available, and have stable CDK constructs in the pinned CDK version—spine’s “as available in aws-cdk-lib 2.262” claim is accurate (now stable, not alpha-only).

3. **Auth pattern is real but not trivial.** Cognito Identity Pool → STS creds → SigV4 to IAM-protected Function URL is the correct pattern when Function URL auth is `AWS_IAM`. Lambda Function URLs do **not** natively accept Cognito User Pool JWTs as SigV4—User Pool tokens must flow through Identity Pool first. The spine’s alternate “Cognito JWT authorizer on the Function URL/API” wording applies to API Gateway or custom in-function validation, not built-in Function URL JWT auth.

4. **Node 22 is valid but not the newest LTS anchor.** Maintenance LTS until 2027-04-30; Node 24 is Active LTS. Acceptable for V1 demo; no change required unless team wants longest LTS runway.

5. **Model access remains an operator gate.** Sonnet 4 inference profile must be enabled in account/region before deploy; spine already captures this in AD-6 assumption and fallback pin—no silent training-data assertion.

6. **No evidence of unverified version invention.** Spine footer date aligns with actual package release dates (CDK 2.262.x and strands 1.47.0 both published within ~2 weeks of review date).

---

## Recommendations (non-blocking)

- When lockfiles land, pin exact patch (e.g. `aws-cdk-lib@2.262.1`, `strands-agents==1.47.0`) and record in repo—not only caret in spine.
- Document Identity Pool IAM role permissions and Function URL CORS for SigV4 preflight in deploy docs (epics/stories).
- Clarify AD-1 auth wording: “JWT authorizer” path implies API Gateway or in-Lambda JWT verify, distinct from Identity Pool + SigV4 on Function URL.

---

## Sources (representative)

- npm: [aws-cdk-lib](https://www.npmjs.com/package/aws-cdk-lib) — 2.262.1
- GitHub: [aws/aws-cdk releases v2.262.x](https://github.com/aws/aws-cdk/releases)
- PyPI: [strands-agents 1.47.0](https://pypi.org/project/strands-agents/1.47.0/)
- AWS: [Claude Sonnet 4 model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-4.html)
- AWS: [AgentCore what is](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html)
- AWS: [AgentCore regions](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-regions.html)
- AWS CDK: [aws_bedrockagentcore construct library 2.262.1](https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_bedrockagentcore/README.html)
- Node: [nodejs/Release README](https://github.com/nodejs/release/blob/main/README.md) — 22.x Maintenance LTS
- AWS Lambda: [Python runtimes](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)
- AWS: [Lambda Function URL auth](https://docs.aws.amazon.com/lambda/latest/dg/urls-auth.html); [Cognito identity pool credentials](https://docs.aws.amazon.com/cognito/latest/developerguide/getting-credentials.html)
