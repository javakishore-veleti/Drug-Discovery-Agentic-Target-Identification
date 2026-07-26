/** Browser config — Vite env (local) or `/config.json` (CloudFront / Story 6.2). */

export const DISCLAIMER =
  "Research assistance only. Not medical advice. Verify claims against primary sources (PMID / NCT / ChEMBL IDs). Not for clinical decision-making.";

/** Soft stall budget — NFR-9 / Story 5.4 (matches Stream Lambda 5-minute timeout). */
export const STALL_TIMEOUT_MS = 5 * 60 * 1000;

export type AppConfig = {
  region: string;
  userPoolId: string;
  userPoolClientId: string;
  identityPoolId: string;
  streamUrl: string;
};

function fromEnv(): AppConfig | null {
  const userPoolId = (import.meta.env.VITE_USER_POOL_ID as string | undefined)?.trim();
  const userPoolClientId = (
    import.meta.env.VITE_USER_POOL_CLIENT_ID as string | undefined
  )?.trim();
  const identityPoolId = (
    import.meta.env.VITE_IDENTITY_POOL_ID as string | undefined
  )?.trim();
  const streamUrl = (import.meta.env.VITE_STREAM_URL as string | undefined)?.trim();
  if (!userPoolId || !userPoolClientId || !identityPoolId || !streamUrl) {
    return null;
  }
  return {
    region:
      (import.meta.env.VITE_AWS_REGION as string | undefined)?.trim() || "us-east-1",
    userPoolId,
    userPoolClientId,
    identityPoolId,
    streamUrl,
  };
}

function normalize(raw: Record<string, unknown>): AppConfig {
  const region = String(raw.region || raw.awsRegion || "us-east-1").trim();
  const userPoolId = String(raw.userPoolId || "").trim();
  const userPoolClientId = String(raw.userPoolClientId || "").trim();
  const identityPoolId = String(raw.identityPoolId || "").trim();
  const streamUrl = String(raw.streamUrl || "").trim();
  if (!userPoolId || !userPoolClientId || !identityPoolId || !streamUrl) {
    throw new Error("config.json missing Cognito / Stream fields");
  }
  return { region, userPoolId, userPoolClientId, identityPoolId, streamUrl };
}

/** Prefer hosted config.json (Frontend stack); fall back to Vite env for local dev. */
export async function resolveAppConfig(): Promise<AppConfig> {
  try {
    const resp = await fetch("/config.json", { cache: "no-store" });
    if (resp.ok) {
      return normalize((await resp.json()) as Record<string, unknown>);
    }
  } catch {
    // local / offline — use Vite env
  }
  const envCfg = fromEnv();
  if (envCfg) return envCfg;
  throw new Error(
    "Missing app config. For local: copy web/.env.example → web/.env.local. " +
      "For CloudFront: deploy Frontend stack (injects /config.json).",
  );
}

/** @deprecated use resolveAppConfig — kept for sync call sites during migration */
export function getAppConfig(): AppConfig {
  const envCfg = fromEnv();
  if (!envCfg) {
    throw new Error(
      "Missing VITE_* env. Copy web/.env.example → web/.env.local, or use resolveAppConfig().",
    );
  }
  return envCfg;
}
