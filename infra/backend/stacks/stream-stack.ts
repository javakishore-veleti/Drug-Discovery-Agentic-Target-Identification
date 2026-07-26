import * as path from "path";
import * as cdk from "aws-cdk-lib";
import * as iam from "aws-cdk-lib/aws-iam";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as logs from "aws-cdk-lib/aws-logs";
import { Construct } from "constructs";

export interface StreamStackProps extends cdk.StackProps {
  /** AgentCore Runtime ARN (Stream is the only client path for browsers). */
  readonly agentRuntimeArn: string;
  /** Optional principal allowed to InvokeFunctionUrl (local smoke / Story 4.1). */
  readonly streamInvokerArn?: string;
}

/**
 * Stories 4.1–4.4 — Stream Lambda SSE bridge + IAM Function URL.
 *
 * - Python 3.12 handler under ``stream/``
 * - Emits AD-4 Stream Events; owns sessionId (AD-7)
 * - Clients SigV4 the Function URL — never AgentCore Runtime IAM (AD-1)
 * - Cognito Identity Pool grant is applied from AuthStack (avoids cyclic deps)
 */
export class StreamStack extends cdk.Stack {
  public readonly streamUrl: string;
  public readonly streamFunctionName: string;
  public readonly streamFunction: lambda.IFunction;
  public readonly functionUrl: lambda.FunctionUrl;

  constructor(scope: Construct, id: string, props: StreamStackProps) {
    super(scope, id, props);

    const streamDir = path.join(__dirname, "..", "..", "..", "stream");

    const logGroup = new logs.LogGroup(this, "StreamLogs", {
      retention: logs.RetentionDays.ONE_WEEK,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    const fn = new lambda.Function(this, "StreamFn", {
      functionName: "agentic-target-id-stream",
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: "handler.lambda_handler",
      timeout: cdk.Duration.minutes(5),
      memorySize: 512,
      description:
        "SSE Stream bridge to AgentCore Runtime (Story 4.1) — no browser→Runtime",
      logGroup,
      environment: {
        AGENT_RUNTIME_ARN: props.agentRuntimeArn,
      },
      code: lambda.Code.fromAsset(streamDir, {
        bundling: {
          image: lambda.Runtime.PYTHON_3_12.bundlingImage,
          command: [
            "bash",
            "-c",
            [
              "if [ -f requirements-lambda.txt ]; then pip install -r requirements-lambda.txt -t /asset-output --quiet; fi",
              "cp handler.py /asset-output/",
            ].join(" && "),
          ],
        },
      }),
    });
    this.streamFunction = fn;

    // Only the Stream role invokes Runtime (FR8 / NFR1).
    fn.addToRolePolicy(
      new iam.PolicyStatement({
        sid: "InvokeAgentCoreRuntime",
        actions: ["bedrock-agentcore:InvokeAgentRuntime"],
        resources: [
          props.agentRuntimeArn,
          `${props.agentRuntimeArn}/*`,
        ],
      }),
    );

    const fnUrl = fn.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.AWS_IAM,
      // Python managed runtime does not natively streamifyResponse; return a
      // complete text/event-stream body with ordered AD-4 events (Story 4.1).
      invokeMode: lambda.InvokeMode.BUFFERED,
      cors: {
        allowedOrigins: ["*"],
        allowedMethods: [lambda.HttpMethod.POST],
        allowedHeaders: [
          "authorization",
          "content-type",
          "x-amz-date",
          "x-amz-security-token",
        ],
      },
    });

    const invokerArn =
      props.streamInvokerArn ||
      (this.node.tryGetContext("streamInvokerArn") as string | undefined) ||
      (this.node.tryGetContext("gatewayInvokerArn") as string | undefined) ||
      process.env.STREAM_INVOKER_ARN ||
      process.env.GATEWAY_INVOKER_ARN;

    if (invokerArn) {
      fnUrl.grantInvokeUrl(new iam.ArnPrincipal(invokerArn));
    } else {
      fnUrl.grantInvokeUrl(new iam.AccountRootPrincipal());
    }

    this.functionUrl = fnUrl;
    this.streamUrl = fnUrl.url;
    this.streamFunctionName = fn.functionName;

    new cdk.CfnOutput(this, "StreamUrl", {
      value: fnUrl.url,
      description:
        "IAM-auth Function URL for SSE Stream (SigV4). Not an AgentCore Runtime URL.",
      exportName: "AgenticTargetId-StreamUrl",
    });
    new cdk.CfnOutput(this, "StreamFunctionName", {
      value: fn.functionName,
      description: "Stream Lambda function name",
      exportName: "AgenticTargetId-StreamFunctionName",
    });
    new cdk.CfnOutput(this, "StreamAuthNote", {
      value:
        "Clients SigV4 this StreamUrl via Identity Pool (or ops CLI). Never Runtime IAM in the browser (AD-1).",
      description: "Security reminder for Stories 4.1–4.2",
    });
  }

  /** Grant IAM Function URL invoke (used if Auth is wired after Stream). */
  public grantInvokeUrl(grantee: iam.IGrantable): void {
    this.functionUrl.grantInvokeUrl(grantee);
  }
}
