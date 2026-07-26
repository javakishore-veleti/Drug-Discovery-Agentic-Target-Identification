import * as cdk from "aws-cdk-lib";
import * as cognito from "aws-cdk-lib/aws-cognito";
import {
  IdentityPool,
  UserPoolAuthenticationProvider,
} from "aws-cdk-lib/aws-cognito-identitypool";
import * as iam from "aws-cdk-lib/aws-iam";
import * as lambda from "aws-cdk-lib/aws-lambda";
import { Construct } from "constructs";

export interface AuthStackProps extends cdk.StackProps {
  /**
   * Stream Function URL to grant Identity Pool authenticated role invoke
   * (Story 4.2 / AD-1). Auth depends on Stream — not the reverse — to avoid cycles.
   */
  readonly streamFunctionUrl: lambda.IFunctionUrl;
}

/**
 * Story 4.2 — Cognito User Pool + Identity Pool (AD-1 / AD-10).
 *
 * - Email/password; admin-provisioned users (no self-signup UI)
 * - Identity Pool authenticated role may SigV4 the Stream Function URL
 * - No JWT authorizer on the Function URL (Deferred)
 */
export class AuthStack extends cdk.Stack {
  public readonly userPool: cognito.IUserPool;
  public readonly userPoolClient: cognito.IUserPoolClient;
  public readonly identityPool: IdentityPool;
  public readonly authenticatedRole: iam.IRole;

  constructor(scope: Construct, id: string, props: AuthStackProps) {
    super(scope, id, props);

    const userPool = new cognito.UserPool(this, "UserPool", {
      userPoolName: "agentic-target-id-users",
      selfSignUpEnabled: false,
      signInAliases: { email: true },
      autoVerify: { email: true },
      standardAttributes: {
        email: { required: true, mutable: true },
      },
      passwordPolicy: {
        minLength: 12,
        requireLowercase: true,
        requireUppercase: true,
        requireDigits: true,
        requireSymbols: false,
      },
      accountRecovery: cognito.AccountRecovery.EMAIL_ONLY,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    const userPoolClient = userPool.addClient("AppClient", {
      userPoolClientName: "agentic-target-id-web",
      generateSecret: false,
      authFlows: {
        userPassword: true,
        userSrp: true,
        adminUserPassword: true,
      },
      preventUserExistenceErrors: true,
    });

    const identityPool = new IdentityPool(this, "IdentityPool", {
      identityPoolName: "agentic_target_id_idpool",
      allowUnauthenticatedIdentities: false,
      authenticationProviders: {
        userPools: [
          new UserPoolAuthenticationProvider({
            userPool,
            userPoolClient,
          }),
        ],
      },
    });

    // Identity policy on authenticated role + Function URL resource policy (dual auth).
    props.streamFunctionUrl.grantInvokeUrl(identityPool.authenticatedRole);

    this.userPool = userPool;
    this.userPoolClient = userPoolClient;
    this.identityPool = identityPool;
    this.authenticatedRole = identityPool.authenticatedRole;

    new cdk.CfnOutput(this, "UserPoolId", {
      value: userPool.userPoolId,
      description: "Cognito User Pool id (admin create-user)",
      exportName: "AgenticTargetId-UserPoolId",
    });
    new cdk.CfnOutput(this, "UserPoolClientId", {
      value: userPoolClient.userPoolClientId,
      description: "Cognito app client id (no secret)",
      exportName: "AgenticTargetId-UserPoolClientId",
    });
    new cdk.CfnOutput(this, "IdentityPoolId", {
      value: identityPool.identityPoolId,
      description: "Cognito Identity Pool id (GetCredentialsForIdentity)",
      exportName: "AgenticTargetId-IdentityPoolId",
    });
    new cdk.CfnOutput(this, "AuthenticatedRoleArn", {
      value: identityPool.authenticatedRole.roleArn,
      description: "IAM role assumed by authenticated Identity Pool users",
    });
  }
}
