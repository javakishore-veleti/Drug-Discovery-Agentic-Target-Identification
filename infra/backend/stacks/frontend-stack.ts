import * as fs from "fs";
import * as path from "path";
import { execSync } from "child_process";
import * as cdk from "aws-cdk-lib";
import * as cloudfront from "aws-cdk-lib/aws-cloudfront";
import * as origins from "aws-cdk-lib/aws-cloudfront-origins";
import * as s3 from "aws-cdk-lib/aws-s3";
import * as s3deploy from "aws-cdk-lib/aws-s3-deployment";
import { Construct } from "constructs";

export interface FrontendStackProps extends cdk.StackProps {
  readonly userPoolId: string;
  readonly userPoolClientId: string;
  readonly identityPoolId: string;
  readonly streamUrl: string;
}

/**
 * Story 6.2 — S3 + CloudFront hosting for ``web/`` with injected Cognito/Stream config.
 *
 * App loads ``/config.json`` at runtime (Backend Outputs). HTTPS via CloudFront.
 */
export class FrontendStack extends cdk.Stack {
  public readonly frontendUrl: string;

  constructor(scope: Construct, id: string, props: FrontendStackProps) {
    super(scope, id, props);

    const webDir = path.join(__dirname, "..", "..", "..", "web");
    const region = cdk.Stack.of(this).region;

    const siteBucket = new s3.Bucket(this, "WebBucket", {
      bucketName: undefined, // account-unique generated name
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      encryption: s3.BucketEncryption.S3_MANAGED,
      enforceSSL: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });

    const distribution = new cloudfront.Distribution(this, "WebDistribution", {
      comment: "Agentic Target ID research chat (Story 6.2)",
      defaultRootObject: "index.html",
      minimumProtocolVersion: cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
      defaultBehavior: {
        origin: origins.S3BucketOrigin.withOriginAccessControl(siteBucket),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        allowedMethods: cloudfront.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
        cachedMethods: cloudfront.CachedMethods.CACHE_GET_HEAD_OPTIONS,
        compress: true,
      },
      errorResponses: [
        {
          httpStatus: 403,
          responseHttpStatus: 200,
          responsePagePath: "/index.html",
          ttl: cdk.Duration.minutes(1),
        },
        {
          httpStatus: 404,
          responseHttpStatus: 200,
          responsePagePath: "/index.html",
          ttl: cdk.Duration.minutes(1),
        },
      ],
    });

    const placeholderEnv = {
      VITE_AWS_REGION: region,
      VITE_USER_POOL_ID: "deploy-time",
      VITE_USER_POOL_CLIENT_ID: "deploy-time",
      VITE_IDENTITY_POOL_ID: "deploy-time",
      VITE_STREAM_URL: "https://deploy-time.example/",
    };

    new s3deploy.BucketDeployment(this, "DeployWeb", {
      sources: [
        s3deploy.Source.asset(webDir, {
          exclude: [
            "node_modules",
            "dist",
            ".env",
            ".env.*",
            "!.env.example",
            "*.md",
            "scripts",
          ],
          bundling: {
            image: cdk.DockerImage.fromRegistry(
              "public.ecr.aws/docker/library/node:20-bookworm",
            ),
            environment: placeholderEnv,
            command: [
              "bash",
              "-c",
              [
                "npm ci --ignore-scripts",
                "npm run build",
                "cp -r dist/. /asset-output/",
              ].join(" && "),
            ],
            local: {
              tryBundle(outputDir: string): boolean {
                try {
                  execSync("npm ci --ignore-scripts", {
                    cwd: webDir,
                    stdio: "inherit",
                    env: { ...process.env, ...placeholderEnv },
                  });
                  execSync("npm run build", {
                    cwd: webDir,
                    stdio: "inherit",
                    env: { ...process.env, ...placeholderEnv },
                  });
                  const dist = path.join(webDir, "dist");
                  fs.cpSync(dist, outputDir, { recursive: true });
                  return true;
                } catch (err) {
                  console.warn("Local web bundling failed; Docker may be used:", err);
                  return false;
                }
              },
            },
          },
        }),
        s3deploy.Source.jsonData("config.json", {
          region,
          userPoolId: props.userPoolId,
          userPoolClientId: props.userPoolClientId,
          identityPoolId: props.identityPoolId,
          streamUrl: props.streamUrl,
        }),
      ],
      destinationBucket: siteBucket,
      distribution,
      distributionPaths: ["/*"],
      memoryLimit: 1024,
    });

    this.frontendUrl = `https://${distribution.distributionDomainName}`;

    new cdk.CfnOutput(this, "FrontendUrl", {
      value: this.frontendUrl,
      description:
        "CloudFront HTTPS URL for the research chat UI (Story 6.2 / FR18)",
      exportName: "AgenticTargetId-FrontendUrl",
    });
    new cdk.CfnOutput(this, "WebBucketName", {
      value: siteBucket.bucketName,
      description: "S3 bucket holding the Vite build + config.json",
    });
  }
}
