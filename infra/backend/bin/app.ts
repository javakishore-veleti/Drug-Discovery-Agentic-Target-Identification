#!/usr/bin/env node
import * as cdk from "aws-cdk-lib";
import { AuthStack } from "../stacks/auth-stack";
import { GatewayStack } from "../stacks/gateway-stack";
import { RuntimeStack } from "../stacks/runtime-stack";
import { StreamStack } from "../stacks/stream-stack";

const app = new cdk.App();

const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION || process.env.AWS_REGION || "us-east-1",
};

const invokerArn =
  (app.node.tryGetContext("gatewayInvokerArn") as string | undefined) ||
  process.env.GATEWAY_INVOKER_ARN ||
  process.env.RUNTIME_INVOKER_ARN ||
  process.env.STREAM_INVOKER_ARN;

if (invokerArn) {
  app.node.setContext("gatewayInvokerArn", invokerArn);
}

const gateway = new GatewayStack(app, "AgenticTargetIdGateway", {
  env,
  description:
    "Agentic Target ID — AgentCore Gateway + pubmed/clinicaltrials/chembl (Epic 2)",
});

const runtime = new RuntimeStack(app, "AgenticTargetIdRuntime", {
  env,
  description:
    "Agentic Target ID — AgentCore Runtime + Memory STM (Stories 3.1–3.2)",
  gatewayUrl: gateway.gatewayUrl,
  gatewayArn: gateway.gatewayArn,
  gatewayId: gateway.gatewayId,
  runtimeInvokerArn: invokerArn,
});
runtime.addDependency(gateway);

const stream = new StreamStack(app, "AgenticTargetIdStream", {
  env,
  description:
    "Agentic Target ID — Stream Lambda SSE bridge (Stories 4.1–4.2)",
  agentRuntimeArn: runtime.agentRuntimeArn,
  streamInvokerArn: invokerArn,
});
stream.addDependency(runtime);
// Stream Lambda may InvokeAgentRuntime; browsers never get this grant (AD-1).
runtime.grantInvoke(stream.streamFunction);

// Auth after Stream so Identity Pool role can be granted InvokeFunctionUrl without a cycle.
const auth = new AuthStack(app, "AgenticTargetIdAuth", {
  env,
  description:
    "Agentic Target ID — Cognito User Pool + Identity Pool (Story 4.2 / AD-1)",
  streamFunctionUrl: stream.functionUrl,
});
auth.addDependency(stream);

app.synth();
