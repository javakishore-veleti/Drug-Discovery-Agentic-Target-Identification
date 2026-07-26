import * as path from "path";
import * as cdk from "aws-cdk-lib";
import * as agentcore from "aws-cdk-lib/aws-bedrockagentcore";
import * as iam from "aws-cdk-lib/aws-iam";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as logs from "aws-cdk-lib/aws-logs";
import { Construct } from "constructs";

/**
 * Story 2.1 — AgentCore Gateway scaffold with PubMed as MCP Lambda target.
 *
 * - Inbound auth: AWS IAM (Runtime / local SigV4 clients)
 * - Tool schema name: exactly `pubmed` (AD-3)
 * - Target name: `pubmed` so the Gateway wire name is `pubmed___pubmed`;
 *   the agent normalizes to logical tool `pubmed` when listing/calling.
 */
export class GatewayStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const pubmedCodePath = path.join(
      __dirname,
      "..",
      "..",
      "..",
      "gateways",
      "database",
      "pubmed",
    );

    const pubmedLogGroup = new logs.LogGroup(this, "PubmedToolLogs", {
      retention: logs.RetentionDays.ONE_WEEK,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    const pubmedFn = new lambda.Function(this, "PubmedToolFn", {
      functionName: "agentic-target-id-pubmed",
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: "handler.lambda_handler",
      timeout: cdk.Duration.seconds(45),
      memorySize: 256,
      description: "AgentCore Gateway MCP tool pubmed (shared NCBI adapter)",
      logGroup: pubmedLogGroup,
      code: lambda.Code.fromAsset(pubmedCodePath, {
        bundling: {
          image: lambda.Runtime.PYTHON_3_12.bundlingImage,
          command: [
            "bash",
            "-c",
            [
              "pip install -r requirements-lambda.txt -t /asset-output --quiet",
              "cp -r handler.py adapter.py __init__.py /asset-output/",
            ].join(" && "),
          ],
        },
      }),
      environment: {
        PUBMED_SSL_VERIFY: "true",
      },
    });

    const gateway = new agentcore.Gateway(this, "ResearchGateway", {
      gatewayName: "agentic-target-id-gw",
      description: "Agentic Target ID evidence gateway (V1 PubMed)",
      authorizerConfiguration: agentcore.GatewayAuthorizer.usingAwsIam(),
      exceptionLevel: agentcore.GatewayExceptionLevel.DEBUG,
      protocolConfiguration: agentcore.GatewayProtocol.mcp({
        supportedVersions: [agentcore.MCPProtocolVersion.MCP_2025_03_26],
        instructions:
          "Evidence tools for drug-discovery target identification. Logical tool names: pubmed (then clinicaltrials, chembl).",
      }),
    });

    gateway.addLambdaTarget("PubmedTarget", {
      gatewayTargetName: "pubmed",
      description: "PubMed literature search (NCBI E-utilities)",
      lambdaFunction: pubmedFn,
      toolSchema: agentcore.ToolSchema.fromInline([
        {
          name: "pubmed",
          description:
            "Search PubMed via NCBI E-utilities for biomedical literature. " +
            "Use for mechanism, safety, and target-identification questions. " +
            "Returns status, ids.pmid (string array), and a short summary of hits.",
          inputSchema: {
            type: agentcore.SchemaDefinitionType.OBJECT,
            properties: {
              query: {
                type: agentcore.SchemaDefinitionType.STRING,
                description:
                  "PubMed/Entrez search terms (e.g. trastuzumab mechanism of action).",
              },
              retmax: {
                type: agentcore.SchemaDefinitionType.INTEGER,
                description: "Max PMIDs to return (1–20). Default 8.",
              },
            },
            required: ["query"],
          },
        },
      ]),
    });

    // Local CLI / deploy principal may invoke Gateway via SigV4 (Story 2.1 smoke).
    const invokerArn =
      (this.node.tryGetContext("gatewayInvokerArn") as string | undefined) ||
      process.env.GATEWAY_INVOKER_ARN;
    if (invokerArn) {
      gateway.grantInvoke(new iam.ArnPrincipal(invokerArn));
    } else {
      // Account root — operators attach/assume as needed for demos.
      gateway.grantInvoke(new iam.AccountRootPrincipal());
    }

    new cdk.CfnOutput(this, "GatewayUrl", {
      value: gateway.gatewayUrl ?? "",
      description: "AgentCore Gateway MCP endpoint URL",
      exportName: "AgenticTargetId-GatewayUrl",
    });
    new cdk.CfnOutput(this, "GatewayId", {
      value: gateway.gatewayId,
      description: "AgentCore Gateway identifier",
      exportName: "AgenticTargetId-GatewayId",
    });
    new cdk.CfnOutput(this, "GatewayArn", {
      value: gateway.gatewayArn,
      description: "AgentCore Gateway ARN",
      exportName: "AgenticTargetId-GatewayArn",
    });
    new cdk.CfnOutput(this, "PubmedLambdaName", {
      value: pubmedFn.functionName,
      description: "PubMed tool Lambda name",
    });
    new cdk.CfnOutput(this, "PubmedMcpToolName", {
      value: "pubmed",
      description: "Logical MCP tool name (AD-3). Wire name may be pubmed___pubmed.",
    });
  }
}
