import * as path from "path";
import * as cdk from "aws-cdk-lib";
import * as agentcore from "aws-cdk-lib/aws-bedrockagentcore";
import * as ecr_assets from "aws-cdk-lib/aws-ecr-assets";
import * as iam from "aws-cdk-lib/aws-iam";
import { Construct } from "constructs";

export interface RuntimeStackProps extends cdk.StackProps {
  /** AgentCore Gateway MCP URL (from Gateway stack). */
  readonly gatewayUrl: string;
  /** AgentCore Gateway ARN for IAM grantInvoke. */
  readonly gatewayArn: string;
  /** AgentCore Gateway id. */
  readonly gatewayId: string;
  /** Optional principal ARN allowed to InvokeAgentRuntime (local smoke). */
  readonly runtimeInvokerArn?: string;
}

/**
 * Stories 3.1–3.2 — AgentCore Runtime + in-session Memory (STM).
 *
 * - ARM64 Docker asset from repo-root Dockerfile
 * - BEDROCK_MODEL_ID pin (AD-6 / Sonnet 4.6)
 * - Env AGENTCORE_GATEWAY_URL so tools use Gateway MCP when configured
 * - Env AGENTCORE_MEMORY_ID for Chat Session multi-turn (AD-7; no MEMORY_ID alias)
 */
export class RuntimeStack extends cdk.Stack {
  public readonly agentRuntimeArn: string;
  public readonly agentRuntimeId: string;
  public readonly memoryId: string;
  private readonly runtime: agentcore.Runtime;

  constructor(scope: Construct, id: string, props: RuntimeStackProps) {
    super(scope, id, props);

    const repoRoot = path.join(__dirname, "..", "..", "..");
    const modelId =
      (this.node.tryGetContext("bedrockModelId") as string | undefined) ||
      process.env.BEDROCK_MODEL_ID ||
      "us.anthropic.claude-sonnet-4-6";

    // Story 3.2 — short-term memory only (no LTM strategies / no cross-day UI).
    const memory = new agentcore.Memory(this, "ChatSessionMemory", {
      memoryName: "agentic_target_id_stm",
      description:
        "In-session STM for Unified Research Agent Chat Sessions (AD-7 / Story 3.2)",
      expirationDuration: cdk.Duration.days(7),
    });

    const artifact = agentcore.AgentRuntimeArtifact.fromAsset(repoRoot, {
      file: "agents/unified-research-agent/Dockerfile",
      platform: ecr_assets.Platform.LINUX_ARM64,
    });

    const runtime = new agentcore.Runtime(this, "UnifiedResearchRuntime", {
      runtimeName: "agentic_target_id_ura",
      description:
        "Unified Research Agent (Stories 3.1–3.2) — Runtime + Memory STM",
      agentRuntimeArtifact: artifact,
      networkConfiguration: agentcore.RuntimeNetworkConfiguration.usingPublicNetwork(),
      authorizerConfiguration: agentcore.RuntimeAuthorizerConfiguration.usingIAM(),
      environmentVariables: {
        BEDROCK_MODEL_ID: modelId,
        AWS_DEFAULT_REGION: cdk.Stack.of(this).region,
        AWS_REGION: cdk.Stack.of(this).region,
        AGENTCORE_GATEWAY_URL: props.gatewayUrl,
        USE_GATEWAY_TOOLS: "true",
        AGENTCORE_MEMORY_ID: memory.memoryId,
        AGENTCORE_ACTOR_ID: "agentic_target_id",
      },
    });
    this.runtime = runtime;

    // Bedrock model invoke — cross-region inference profiles (e.g. us.anthropic.*)
    // need foundation-model ARNs in multiple regions; match AWS Runtime IAM guidance.
    runtime.role.addToPrincipalPolicy(
      new iam.PolicyStatement({
        sid: "BedrockModelInvocation",
        actions: [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
        ],
        resources: [
          `arn:${cdk.Stack.of(this).partition}:bedrock:*::foundation-model/*`,
          `arn:${cdk.Stack.of(this).partition}:bedrock:${cdk.Stack.of(this).region}:${cdk.Stack.of(this).account}:inference-profile/*`,
          `arn:${cdk.Stack.of(this).partition}:bedrock:${cdk.Stack.of(this).region}:${cdk.Stack.of(this).account}:application-inference-profile/*`,
          `arn:${cdk.Stack.of(this).partition}:bedrock:${cdk.Stack.of(this).region}:${cdk.Stack.of(this).account}:*`,
        ],
      }),
    );

    // Gateway MCP via SigV4 (mcp-proxy-for-aws → bedrock-agentcore:InvokeGateway)
    runtime.role.addToPrincipalPolicy(
      new iam.PolicyStatement({
        sid: "InvokeAgentCoreGateway",
        actions: ["bedrock-agentcore:InvokeGateway"],
        resources: [props.gatewayArn, `${props.gatewayArn}/*`],
      }),
    );

    // Memory STM read/write for CreateEvent + ListEvents (session history reload)
    memory.grantWrite(runtime.grantPrincipal);
    memory.grantReadShortTermMemory(runtime.grantPrincipal);

    const invokerArn =
      props.runtimeInvokerArn ||
      (this.node.tryGetContext("runtimeInvokerArn") as string | undefined) ||
      process.env.RUNTIME_INVOKER_ARN ||
      process.env.GATEWAY_INVOKER_ARN;
    if (invokerArn) {
      runtime.grantInvoke(new iam.ArnPrincipal(invokerArn));
    } else {
      runtime.grantInvoke(new iam.AccountRootPrincipal());
    }

    this.agentRuntimeArn = runtime.agentRuntimeArn;
    this.agentRuntimeId = runtime.agentRuntimeId;
    this.memoryId = memory.memoryId;

    new cdk.CfnOutput(this, "AgentRuntimeArn", {
      value: runtime.agentRuntimeArn,
      description: "AgentCore Runtime ARN for InvokeAgentRuntime",
      exportName: "AgenticTargetId-AgentRuntimeArn",
    });
    new cdk.CfnOutput(this, "AgentRuntimeId", {
      value: runtime.agentRuntimeId,
      description: "AgentCore Runtime id",
      exportName: "AgenticTargetId-AgentRuntimeId",
    });
    new cdk.CfnOutput(this, "BedrockModelId", {
      value: modelId,
      description: "Pinned BEDROCK_MODEL_ID (AD-6)",
    });
    new cdk.CfnOutput(this, "RuntimeGatewayUrl", {
      value: props.gatewayUrl,
      description: "AGENTCORE_GATEWAY_URL configured on the Runtime",
    });
    new cdk.CfnOutput(this, "RuntimeGatewayId", {
      value: props.gatewayId,
      description: "Gateway id paired with this Runtime",
    });
    new cdk.CfnOutput(this, "AgentCoreMemoryId", {
      value: memory.memoryId,
      description: "AGENTCORE_MEMORY_ID for Chat Session STM (Story 3.2)",
      exportName: "AgenticTargetId-AgentCoreMemoryId",
    });
  }

  /** Allow Stream Lambda (or other backends) to InvokeAgentRuntime — not browsers. */
  public grantInvoke(grantee: iam.IGrantable): void {
    this.runtime.grantInvoke(grantee);
  }
}
