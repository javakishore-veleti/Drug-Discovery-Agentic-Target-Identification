#!/usr/bin/env node
import * as cdk from "aws-cdk-lib";
import { GatewayStack } from "../stacks/gateway-stack";

const app = new cdk.App();

const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION || process.env.AWS_REGION || "us-east-1",
};

new GatewayStack(app, "AgenticTargetIdGateway", {
  env,
  description: "Agentic Target ID — AgentCore Gateway + PubMed MCP tool (Story 2.1)",
});

app.synth();
