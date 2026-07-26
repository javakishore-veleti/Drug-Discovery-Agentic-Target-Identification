import * as path from "path";
import * as cdk from "aws-cdk-lib";
import * as agentcore from "aws-cdk-lib/aws-bedrockagentcore";
import * as iam from "aws-cdk-lib/aws-iam";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as logs from "aws-cdk-lib/aws-logs";
import { Construct } from "constructs";

/**
 * AgentCore Gateway — PubMed (2.1) + ClinicalTrials.gov (2.2) + ChEMBL (2.3).
 *
 * - Inbound auth: AWS IAM (Runtime / local SigV4 clients)
 * - Tool schema names: exactly `pubmed`, `clinicaltrials`, `chembl` (AD-3)
 * - Wire names may be `${target}___${tool}`; agent normalizes to logical names.
 */
export class GatewayStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const gatewaysDb = path.join(__dirname, "..", "..", "..", "gateways", "database");

    const gateway = new agentcore.Gateway(this, "ResearchGateway", {
      gatewayName: "agentic-target-id-gw",
      description: "Agentic Target ID evidence gateway (V1 pubmed + clinicaltrials + chembl)",
      authorizerConfiguration: agentcore.GatewayAuthorizer.usingAwsIam(),
      exceptionLevel: agentcore.GatewayExceptionLevel.DEBUG,
      protocolConfiguration: agentcore.GatewayProtocol.mcp({
        supportedVersions: [agentcore.MCPProtocolVersion.MCP_2025_03_26],
        instructions:
          "Evidence tools for drug-discovery target identification. Logical tool names: pubmed, clinicaltrials, chembl.",
      }),
    });

    const pubmedFn = this.addToolLambda({
      id: "Pubmed",
      functionName: "agentic-target-id-pubmed",
      codePath: path.join(gatewaysDb, "pubmed"),
      description: "AgentCore Gateway MCP tool pubmed (shared NCBI adapter)",
      env: { PUBMED_SSL_VERIFY: "true" },
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

    const clinicaltrialsFn = this.addToolLambda({
      id: "Clinicaltrials",
      functionName: "agentic-target-id-clinicaltrials",
      codePath: path.join(gatewaysDb, "clinicaltrials"),
      description: "AgentCore Gateway MCP tool clinicaltrials (CT.gov API v2)",
      env: { CLINICALTRIALS_SSL_VERIFY: "true" },
    });

    gateway.addLambdaTarget("ClinicaltrialsTarget", {
      gatewayTargetName: "clinicaltrials",
      description: "ClinicalTrials.gov study search (API v2)",
      lambdaFunction: clinicaltrialsFn,
      toolSchema: agentcore.ToolSchema.fromInline([
        {
          name: "clinicaltrials",
          description:
            "Search ClinicalTrials.gov for interventional/observational studies. " +
            "Use for trial context, HER2/Herceptin-related studies, and NCT IDs. " +
            "Returns status, ids.nct (string array of NCT########), and a short summary.",
          inputSchema: {
            type: agentcore.SchemaDefinitionType.OBJECT,
            properties: {
              query: {
                type: agentcore.SchemaDefinitionType.STRING,
                description:
                  "ClinicalTrials.gov search terms (e.g. trastuzumab HER2 breast cancer).",
              },
              retmax: {
                type: agentcore.SchemaDefinitionType.INTEGER,
                description: "Max NCT IDs to return (1–20). Default 8.",
              },
            },
            required: ["query"],
          },
        },
      ]),
    });

    const chemblFn = this.addToolLambda({
      id: "Chembl",
      functionName: "agentic-target-id-chembl",
      codePath: path.join(gatewaysDb, "chembl"),
      description: "AgentCore Gateway MCP tool chembl (EBI ChEMBL API)",
      env: { CHEMBL_SSL_VERIFY: "true" },
    });

    gateway.addLambdaTarget("ChemblTarget", {
      gatewayTargetName: "chembl",
      description: "ChEMBL molecule / bioactivity search",
      lambdaFunction: chemblFn,
      toolSchema: agentcore.ToolSchema.fromInline([
        {
          name: "chembl",
          description:
            "Search ChEMBL for molecules and drug identities. " +
            "Use for chemistry / bioactivity context (e.g. trastuzumab, HER2 ADCs). " +
            "Returns status, ids.chembl (CHEMBL##### string array), and a short summary.",
          inputSchema: {
            type: agentcore.SchemaDefinitionType.OBJECT,
            properties: {
              query: {
                type: agentcore.SchemaDefinitionType.STRING,
                description: "ChEMBL search terms (e.g. trastuzumab).",
              },
              retmax: {
                type: agentcore.SchemaDefinitionType.INTEGER,
                description: "Max ChEMBL IDs to return (1–20). Default 8.",
              },
            },
            required: ["query"],
          },
        },
      ]),
    });

    const invokerArn =
      (this.node.tryGetContext("gatewayInvokerArn") as string | undefined) ||
      process.env.GATEWAY_INVOKER_ARN;
    if (invokerArn) {
      gateway.grantInvoke(new iam.ArnPrincipal(invokerArn));
    } else {
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
    new cdk.CfnOutput(this, "ClinicaltrialsLambdaName", {
      value: clinicaltrialsFn.functionName,
      description: "ClinicalTrials.gov tool Lambda name",
    });
    new cdk.CfnOutput(this, "ChemblLambdaName", {
      value: chemblFn.functionName,
      description: "ChEMBL tool Lambda name",
    });
    new cdk.CfnOutput(this, "PubmedMcpToolName", {
      value: "pubmed",
      description: "Logical MCP tool name (AD-3).",
    });
    new cdk.CfnOutput(this, "ClinicaltrialsMcpToolName", {
      value: "clinicaltrials",
      description: "Logical MCP tool name (AD-3).",
    });
    new cdk.CfnOutput(this, "ChemblMcpToolName", {
      value: "chembl",
      description: "Logical MCP tool name (AD-3). Wire may be chembl___chembl.",
    });
  }

  private addToolLambda(opts: {
    id: string;
    functionName: string;
    codePath: string;
    description: string;
    env: Record<string, string>;
  }): lambda.Function {
    const logGroup = new logs.LogGroup(this, `${opts.id}ToolLogs`, {
      retention: logs.RetentionDays.ONE_WEEK,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    return new lambda.Function(this, `${opts.id}ToolFn`, {
      functionName: opts.functionName,
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: "handler.lambda_handler",
      timeout: cdk.Duration.seconds(45),
      memorySize: 256,
      description: opts.description,
      logGroup,
      code: lambda.Code.fromAsset(opts.codePath, {
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
      environment: opts.env,
    });
  }
}
