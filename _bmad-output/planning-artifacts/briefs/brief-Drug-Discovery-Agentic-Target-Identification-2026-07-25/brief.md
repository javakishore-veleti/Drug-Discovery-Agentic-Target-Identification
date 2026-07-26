---
title: "Product Brief: Agentic Target ID"
status: final
created: 2026-07-25
updated: 2026-07-25
---

# Product Brief: Agentic Target ID

**Working name:** Agentic Target ID  
**Full / repo name:** Drug Discovery Agentic Target Identification

## Executive Summary

Agentic Target ID is an AWS-native research copilot for early drug-discovery **target identification**. Scientists chat with a unified research agent on Amazon Bedrock AgentCore; the agent calls public biomedical tools through an MCP-style AgentCore Gateway and synthesizes evidence on mechanism, safety, pathways, patient risk, and design hypotheses.

V1 is a deployable vertical slice—not a 30+ tool suite: authenticated streaming chat, AgentCore Runtime + Gateway, a small real tool set (PubMed, ClinicalTrials.gov, ChEMBL), session memory, and CDK deploy/destroy. It is productized desk research for target exploration—not clinical decision support and not a proprietary validated-target platform.

## The Problem

Target identification sits early in the pipeline and absorbs disproportionate cost and failure risk. Evidence that would justify (or kill) a target is scattered across literature, trial registries, chemistry databases, protein networks, and safety sources. Scientists stitch answers by hand; multi-domain questions (e.g. Herceptin mechanism → cardiotoxicity risk → pathway context → safer targeting ideas) take hours of fragmented search with weak source traceability.

Existing alternatives overwhelm with breadth, lock into licensed graphs and enterprise contracts, or stop at static data portals. Missing for many teams—and for builders learning AgentCore—is a **governed, forkable, AWS-native vertical slice**: chat + streaming tool use + a small real tool set + clean lifecycle, without fake “enterprise validated” claims.

## The Solution

Researchers sign in, open a chat session, and ask target-identification questions in natural language. The Unified Research Agent plans tool use, calls biomedical APIs via AgentCore Gateway, streams tool activity and the synthesized answer, and retains multi-turn session context.

V1 centers on a Herceptin / HER2 demo: mechanism, cardiotoxicity / patient-risk framing, pathway context, and safer-targeting hypotheses—grounded only in **public** APIs and scoped as research assistance, not medical advice.

## What Makes This Different

AWS-native governed research copilot that unifies public biomedical evidence through AgentCore + MCP—forkable discovery desk research, not a BenchSci / Insilico-grade validated target platform.

| Win on | Do not claim |
| --- | --- |
| Time-to-pilot after CDK deploy | Proprietary knowledge graph |
| Streaming tool-use transparency | Closed-access literature corpus |
| Clean CDK deploy / destroy (cost-conscious) | Clinical-grade target ranking |
| Add a new gateway tool in under a day | Replacement for experimental validation |

Named comps (Biomni/Phylo, BenchSci, FutureHouse, Open Targets) set bars for breadth or validation depth. This product competes on **AgentCore plumbing, governance shape, and shippable vertical slice**—not on biology moat.

## Who This Serves

**Primary:** Drug discovery scientists and computational biologists exploring targets—desk research, hypothesis generation, evidence synthesis. Demo persona: Herceptin / HER2 safety and design questions.

**Secondary:** The builder/operator who needs an end-to-end AgentCore platform to deploy, demo, tear down, and extend.

**Explicitly not for:** Real clinical decision-making, PHI / patient records, or pipeline go/no-go authority without human scientific review.

## Success Criteria

**V1 “done”**

1. Deploy to the owner’s AWS account with CDK  
2. Log in, ask a Herceptin-style question, see `tool_use` + answer stream  
3. Multi-turn session remembers context  
4. Destroy stacks cleanly  
5. Add one new tool in under a day  

**V1 metrics**

- End-to-end demo works in **<15 minutes** after deploy  
- At least **3** tools callable via the gateway  
- Clear docs for install / deploy / destroy  
- Demo answers surface source identifiers (PMID, NCT ID, ChEMBL ID) enough to spot-check claims  

## Scope

### In for V1

- Cognito email/password auth (no Midway / Federate)  
- React chat UI with streaming; S3 + CloudFront hosting  
- Stream Lambda → Bedrock AgentCore Runtime  
- Unified Research Agent (Python / Strands / Claude on Bedrock)  
- AgentCore Gateway with **3–5** tools: PubMed, ClinicalTrials.gov, ChEMBL first  
- Session memory  
- CDK deploy and destroy in `us-east-1` (or account default) with Bedrock model access  
- Must-use AWS: Bedrock + AgentCore Runtime, AgentCore Gateway (MCP), Cognito, Lambda stream path, CDK, S3 / CloudFront  
- Technical/professional docs and branding; honest scope language  

### Out of V1

- Federate / Midway SSO  
- USPTO (optional later)  
- FAERS / Athena and heavy safety data pipelines  
- Multi-agent swarm in production  
- Heavy WAF / CI polish beyond what the slice needs  
- Proprietary sample code copy from external AgentCore samples (patterns only)  
- PHI, clinical systems, or “enterprise validated” marketing claims  

## Vision

After V1, near-term development prioritizes Open Targets–style structured target evidence and pathway tools before multi-agent orchestration. Over 2–3 years the platform can become a composable AWS life-sciences research agent pattern: fork the slice, plug tools via MCP, keep evidence synthesis transparent—still public-API-first desk research with humans in the loop.

## Constraints & Operating Model

- Region: `us-east-1` or account default; Bedrock model access required  
- Public biomedical APIs only; no real patient data  
- Cost-conscious: tear down when not demoing; no hard launch deadline  
