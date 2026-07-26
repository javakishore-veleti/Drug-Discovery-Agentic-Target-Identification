/** Browser config from Vite env (Auth + Stream stack outputs). */

export const DISCLAIMER =
  "Research assistance only. Not medical advice. Verify claims against primary sources (PMID / NCT / ChEMBL IDs). Not for clinical decision-making.";

/** Soft stall budget — NFR-9 / Story 5.4 (matches Stream Lambda 5-minute timeout). */
export const STALL_TIMEOUT_MS = 5 * 60 * 1000;

function required(name: string): string {
  const val = (import.meta.env[name] as string | undefined)?.trim() ?? "";
  if (!val) {
    throw new Error(
      `Missing ${name}. Copy web/.env.example → web/.env.local and fill Auth/Stream outputs.`,
    );
  }
  return val;
}

export function getAppConfig() {
  return {
    region: (import.meta.env.VITE_AWS_REGION as string | undefined)?.trim() || "us-east-1",
    userPoolId: required("VITE_USER_POOL_ID"),
    userPoolClientId: required("VITE_USER_POOL_CLIENT_ID"),
    identityPoolId: required("VITE_IDENTITY_POOL_ID"),
    streamUrl: required("VITE_STREAM_URL"),
  };
}

export type AppConfig = ReturnType<typeof getAppConfig>;
