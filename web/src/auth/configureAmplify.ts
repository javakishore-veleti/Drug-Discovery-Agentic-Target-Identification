import { Amplify } from "aws-amplify";
import type { AppConfig } from "../config";

let configured = false;

/** Cognito User Pool + Identity Pool (AD-1 / AD-10). No self-signup. */
export function configureAmplify(cfg: AppConfig): void {
  if (configured) return;
  Amplify.configure({
    Auth: {
      Cognito: {
        userPoolId: cfg.userPoolId,
        userPoolClientId: cfg.userPoolClientId,
        identityPoolId: cfg.identityPoolId,
        loginWith: { email: true },
      },
    },
  });
  configured = true;
}
