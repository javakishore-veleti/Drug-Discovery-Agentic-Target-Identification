import * as path from "path";
import * as cdk from "aws-cdk-lib";
import * as agentcore from "aws-cdk-lib/aws-bedrockagentcore";
import * as iam from "aws-cdk-lib/aws-iam";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as logs from "aws-cdk-lib/aws-logs";
import { Construct } from "constructs";

/** Story 2.4 / AD-3 / FR-16 — default Gateway exposes exactly these logical MCP names. */
const V1_LOGICAL_TOOLS = ["pubmed", "clinicaltrials", "chembl"] as const;
/** Story M3.3 — optional fourth tool when ``-c enableTool4=true``. */
const TOOL4_NAME = "opentargets";

/**
 * AgentCore Gateway — V1 evidence tools (Stories 2.1–2.4).
 *
 * - Inbound auth: AWS IAM (Runtime / local SigV4 clients)
 * - Tool schema names: exactly the three names in V1_LOGICAL_TOOLS (AD-3)
 * - Wire names may be `${target}___${tool}`; agent normalizes to logical names.
 * - Shared error contract: docs/tool-result-contract.md
 */
export class GatewayStack extends cdk.Stack {
  /** MCP endpoint URL for Runtime / local SigV4 clients. */
  public readonly gatewayUrl: string;
  /** Gateway ARN for IAM grants. */
  public readonly gatewayArn: string;
  /** Gateway identifier. */
  public readonly gatewayId: string;
  /** Tool Lambda names for ops dashboards/alarms (M1.3 / M1.4). */
  public readonly toolFunctionNames: string[] = [];

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Compile-time guard: do not silently grow past three V1 tools.
    if (V1_LOGICAL_TOOLS.length !== 3) {
      throw new Error("V1_LOGICAL_TOOLS must contain exactly three tool names");
    }

    const gatewaysDb = path.join(__dirname, "..", "..", "..", "gateways", "database");

    const gateway = new agentcore.Gateway(this, "ResearchGateway", {
      gatewayName: "agentic-target-id-gw",
      description: "Agentic Target ID evidence gateway (V1: pubmed, clinicaltrials, chembl)",
      authorizerConfiguration: agentcore.GatewayAuthorizer.usingAwsIam(),
      exceptionLevel: agentcore.GatewayExceptionLevel.DEBUG,
      protocolConfiguration: agentcore.GatewayProtocol.mcp({
        supportedVersions: [agentcore.MCPProtocolVersion.MCP_2025_03_26],
        instructions:
          "Evidence tools for drug-discovery target identification. " +
          `Logical tool names (exactly three): ${V1_LOGICAL_TOOLS.join(", ")}.`,
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

    this.gatewayUrl = gateway.gatewayUrl ?? "";
    this.gatewayArn = gateway.gatewayArn;
    this.gatewayId = gateway.gatewayId;
    this.toolFunctionNames.push(
      pubmedFn.functionName,
      clinicaltrialsFn.functionName,
      chemblFn.functionName,
    );

    // Story M3.3 — optional Open Targets tool (default OFF to keep FR-16 = 3 tools).
    const enableTool4 =
      this.node.tryGetContext("enableTool4") === true ||
      this.node.tryGetContext("enableTool4") === "true";
    let opentargetsFnName = "(disabled)";
    if (enableTool4) {
      const opentargetsFn = this.addToolLambda({
        id: "Opentargets",
        functionName: "agentic-target-id-opentargets",
        codePath: path.join(gatewaysDb, "opentargets"),
        description: "AgentCore Gateway MCP tool opentargets (Open Targets Platform)",
        env: { OPENTARGETS_SSL_VERIFY: "true" },
      });
      gateway.addLambdaTarget("OpentargetsTarget", {
        gatewayTargetName: TOOL4_NAME,
        description: "Open Targets Platform target search (Ensembl ids)",
        lambdaFunction: opentargetsFn,
        toolSchema: agentcore.ToolSchema.fromInline([
          {
            name: TOOL4_NAME,
            description:
              "Search Open Targets Platform for target evidence. " +
              "Use for ERBB2/HER2-style target questions. " +
              "Returns status, ids.ensembl (ENSG…), and a short summary.",
            inputSchema: {
              type: agentcore.SchemaDefinitionType.OBJECT,
              properties: {
                query: {
                  type: agentcore.SchemaDefinitionType.STRING,
                  description: "Target / disease search terms (e.g. ERBB2, HER2).",
                },
                retmax: {
                  type: agentcore.SchemaDefinitionType.INTEGER,
                  description: "Max hits to return (1–20). Default 8.",
                },
              },
              required: ["query"],
            },
          },
        ]),
      });
      this.toolFunctionNames.push(opentargetsFn.functionName);
      opentargetsFnName = opentargetsFn.functionName;
    }

    const invokerArn =
      (this.node.tryGetContext("gatewayInvokerArn") as string | undefined) ||
      process.env.GATEWAY_INVOKER_ARN;
    if (invokerArn) {
      gateway.grantInvoke(new iam.ArnPrincipal(invokerArn));
    } else {
      gateway.grantInvoke(new iam.AccountRootPrincipal());
    }

    new cdk.CfnOutput(this, "GatewayUrl", {
      value: this.gatewayUrl,
      description: "AgentCore Gateway MCP endpoint URL",
      exportName: "AgenticTargetId-GatewayUrl",
    });
    new cdk.CfnOutput(this, "GatewayId", {
      value: this.gatewayId,
      description: "AgentCore Gateway identifier",
      exportName: "AgenticTargetId-GatewayId",
    });
    new cdk.CfnOutput(this, "GatewayArn", {
      value: this.gatewayArn,
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
    new cdk.CfnOutput(this, "V1LogicalTools", {
      value: enableTool4
        ? [...V1_LOGICAL_TOOLS, TOOL4_NAME].join(",")
        : V1_LOGICAL_TOOLS.join(","),
      description:
        "Gateway logical tools (FR-16 default = 3; +opentargets when enableTool4=true)",
    });
    new cdk.CfnOutput(this, "EnableTool4", {
      value: enableTool4 ? "true" : "false",
      description: "Story M3.3 — Open Targets tool enabled via -c enableTool4=true",
    });
    new cdk.CfnOutput(this, "OpentargetsLambdaName", {
      value: opentargetsFnName,
      description: "Open Targets tool Lambda name (or disabled)",
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
