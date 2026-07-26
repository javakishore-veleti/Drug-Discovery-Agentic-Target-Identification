import * as cdk from "aws-cdk-lib";
import * as cloudwatch from "aws-cdk-lib/aws-cloudwatch";
import * as cloudwatch_actions from "aws-cdk-lib/aws-cloudwatch-actions";
import * as sns from "aws-cdk-lib/aws-sns";
import * as subscriptions from "aws-cdk-lib/aws-sns-subscriptions";
import { Construct } from "constructs";

export interface OpsStackProps extends cdk.StackProps {
  readonly streamFunctionName: string;
  readonly toolFunctionNames: string[];
  /** Optional email for alarm SNS (context `opsAlertEmail` or env OPS_ALERT_EMAIL). */
  readonly alertEmail?: string;
}

/**
 * Stories M1.3 / M1.4 — CloudWatch dashboard + optional SNS alarms.
 *
 * No Grafana/ELK. Alarms are optional for destroy-when-idle demos; enable an
 * email via ``-c opsAlertEmail=you@example.com`` when stacks stay up.
 */
export class OpsStack extends cdk.Stack {
  public readonly dashboardName: string;
  public readonly alertTopicArn: string;

  constructor(scope: Construct, id: string, props: OpsStackProps) {
    super(scope, id, props);

    const topic = new sns.Topic(this, "OpsAlerts", {
      displayName: "Agentic Target ID ops alerts (M1.4)",
      topicName: "agentic-target-id-ops-alerts",
    });
    this.alertTopicArn = topic.topicArn;

    const email =
      props.alertEmail ||
      (this.node.tryGetContext("opsAlertEmail") as string | undefined) ||
      process.env.OPS_ALERT_EMAIL;
    if (email) {
      topic.addSubscription(new subscriptions.EmailSubscription(email));
    }

    const streamErrors = new cloudwatch.Metric({
      namespace: "AWS/Lambda",
      metricName: "Errors",
      dimensionsMap: { FunctionName: props.streamFunctionName },
      statistic: "Sum",
      period: cdk.Duration.minutes(5),
    });
    const streamDuration = new cloudwatch.Metric({
      namespace: "AWS/Lambda",
      metricName: "Duration",
      dimensionsMap: { FunctionName: props.streamFunctionName },
      statistic: "p95",
      period: cdk.Duration.minutes(5),
    });
    const streamThrottles = new cloudwatch.Metric({
      namespace: "AWS/Lambda",
      metricName: "Throttles",
      dimensionsMap: { FunctionName: props.streamFunctionName },
      statistic: "Sum",
      period: cdk.Duration.minutes(5),
    });
    const customTurnErrors = new cloudwatch.Metric({
      namespace: "AgenticTargetId/Stream",
      metricName: "TurnErrors",
      dimensionsMap: { FunctionName: props.streamFunctionName },
      statistic: "Sum",
      period: cdk.Duration.minutes(5),
    });

    const dashboard = new cloudwatch.Dashboard(this, "OpsDashboard", {
      dashboardName: "AgenticTargetId-Ops",
    });
    this.dashboardName = "AgenticTargetId-Ops";

    dashboard.addWidgets(
      new cloudwatch.GraphWidget({
        title: "Stream Lambda Errors",
        left: [streamErrors],
        width: 12,
      }),
      new cloudwatch.GraphWidget({
        title: "Stream Lambda Duration p95 (ms)",
        left: [streamDuration],
        width: 12,
      }),
    );
    dashboard.addWidgets(
      new cloudwatch.GraphWidget({
        title: "Stream Throttles",
        left: [streamThrottles],
        width: 12,
      }),
      new cloudwatch.GraphWidget({
        title: "Custom TurnErrors (EMF)",
        left: [customTurnErrors],
        width: 12,
      }),
    );

    const toolErrorMetrics = props.toolFunctionNames.map(
      (name) =>
        new cloudwatch.Metric({
          namespace: "AWS/Lambda",
          metricName: "Errors",
          dimensionsMap: { FunctionName: name },
          statistic: "Sum",
          period: cdk.Duration.minutes(5),
          label: name,
        }),
    );
    if (toolErrorMetrics.length) {
      dashboard.addWidgets(
        new cloudwatch.GraphWidget({
          title: "Gateway tool Lambda Errors",
          left: toolErrorMetrics,
          width: 24,
        }),
      );
    }

    const streamErrorAlarm = new cloudwatch.Alarm(this, "StreamErrorsAlarm", {
      alarmName: "agentic-target-id-stream-errors",
      alarmDescription:
        "Stream Lambda Errors > 0 in 5 minutes (M1.4). Optional while destroy-when-idle.",
      metric: streamErrors,
      threshold: 1,
      evaluationPeriods: 1,
      datapointsToAlarm: 1,
      comparisonOperator:
        cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
      treatMissingData: cloudwatch.TreatMissingData.NOT_BREACHING,
    });
    streamErrorAlarm.addAlarmAction(new cloudwatch_actions.SnsAction(topic));

    // Aggregate tool errors: alarm if any named tool Lambda errors.
    props.toolFunctionNames.forEach((name, idx) => {
      const alarm = new cloudwatch.Alarm(this, `ToolErrorsAlarm${idx}`, {
        alarmName: `agentic-target-id-tool-errors-${name.replace(/[^a-z0-9-]/gi, "")}`,
        alarmDescription: `Tool Lambda ${name} Errors ≥ 1 in 5 minutes (M1.4)`,
        metric: new cloudwatch.Metric({
          namespace: "AWS/Lambda",
          metricName: "Errors",
          dimensionsMap: { FunctionName: name },
          statistic: "Sum",
          period: cdk.Duration.minutes(5),
        }),
        threshold: 1,
        evaluationPeriods: 1,
        datapointsToAlarm: 1,
        comparisonOperator:
          cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
        treatMissingData: cloudwatch.TreatMissingData.NOT_BREACHING,
      });
      alarm.addAlarmAction(new cloudwatch_actions.SnsAction(topic));
    });

    new cdk.CfnOutput(this, "OpsDashboardName", {
      value: this.dashboardName,
      description: "CloudWatch dashboard name (M1.3). Open in CW console.",
      exportName: "AgenticTargetId-OpsDashboardName",
    });
    new cdk.CfnOutput(this, "OpsDashboardUrl", {
      value: `https://${this.region}.console.aws.amazon.com/cloudwatch/home?region=${this.region}#dashboards:name=${this.dashboardName}`,
      description: "Console deep link to ops dashboard",
    });
    new cdk.CfnOutput(this, "OpsAlertTopicArn", {
      value: topic.topicArn,
      description:
        "SNS topic for Stream/tool alarms (M1.4). Confirm email if opsAlertEmail set.",
      exportName: "AgenticTargetId-OpsAlertTopicArn",
    });
    new cdk.CfnOutput(this, "OpsAlertEmailNote", {
      value: email
        ? `Subscription pending confirmation for ${email}`
        : "No opsAlertEmail — alarms publish to SNS topic only. Pass -c opsAlertEmail=you@example.com",
      description: "How to receive alarm email",
    });
  }
}
