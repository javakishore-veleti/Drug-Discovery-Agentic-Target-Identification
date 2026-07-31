/** Browser config — Vite env (local) or `/config.json` (CloudFront / Story 6.2). */

export const DISCLAIMER =
  "Research assistance only. Not medical advice. Verify claims against primary sources (PMID / NCT / ChEMBL IDs). Not for clinical decision-making.";

/** Soft stall budget — NFR-9 / Story 5.4 (matches Stream Lambda 5-minute timeout). */
export const STALL_TIMEOUT_MS = 5 * 60 * 1000;

export type StackMode = "local" | "aws";

export type AppConfig = {
  mode: StackMode;
  region: string;
  streamUrl: string;
  /** Cognito — required only when mode === "aws" */
  userPoolId: string;
  userPoolClientId: string;
  identityPoolId: string;
};

const LOCAL_STREAM_DEFAULT = "http://127.0.0.1:8787/";

function stackModeFrom(raw: string | undefined): StackMode {
  const v = (raw || "").trim().toLowerCase();
  if (v === "local" || v === "dev" || v === "offline") return "local";
  return "aws";
}

function fromEnv(): AppConfig | null {
  const mode = stackModeFrom(import.meta.env.VITE_STACK_MODE as string | undefined);
  const streamUrl =
    (import.meta.env.VITE_STREAM_URL as string | undefined)?.trim() ||
    (mode === "local" ? LOCAL_STREAM_DEFAULT : "");
  const region =
    (import.meta.env.VITE_AWS_REGION as string | undefined)?.trim() || "us-east-1";

  if (mode === "local") {
    if (!streamUrl) return null;
    return {
      mode: "local",
      region,
      streamUrl,
      userPoolId: "",
      userPoolClientId: "",
      identityPoolId: "",
    };
  }

  const userPoolId = (import.meta.env.VITE_USER_POOL_ID as string | undefined)?.trim();
  const userPoolClientId = (
    import.meta.env.VITE_USER_POOL_CLIENT_ID as string | undefined
  )?.trim();
  const identityPoolId = (
    import.meta.env.VITE_IDENTITY_POOL_ID as string | undefined
  )?.trim();
  if (!userPoolId || !userPoolClientId || !identityPoolId || !streamUrl) {
    return null;
  }
  return {
    mode: "aws",
    region,
    userPoolId,
    userPoolClientId,
    identityPoolId,
    streamUrl,
  };
}

function normalize(raw: Record<string, unknown>): AppConfig {
  const mode = stackModeFrom(
    String(raw.mode || raw.stackMode || import.meta.env.VITE_STACK_MODE || "aws"),
  );
  const region = String(raw.region || raw.awsRegion || "us-east-1").trim();
  const streamUrl =
    String(raw.streamUrl || "").trim() ||
    (mode === "local" ? LOCAL_STREAM_DEFAULT : "");
  if (mode === "local") {
    if (!streamUrl) throw new Error("config.json missing streamUrl for local mode");
    return {
      mode: "local",
      region,
      streamUrl,
      userPoolId: "",
      userPoolClientId: "",
      identityPoolId: "",
    };
  }
  const userPoolId = String(raw.userPoolId || "").trim();
  const userPoolClientId = String(raw.userPoolClientId || "").trim();
  const identityPoolId = String(raw.identityPoolId || "").trim();
  if (!userPoolId || !userPoolClientId || !identityPoolId || !streamUrl) {
    throw new Error("config.json missing Cognito / Stream fields");
  }
  return {
    mode: "aws",
    region,
    userPoolId,
    userPoolClientId,
    identityPoolId,
    streamUrl,
  };
}

/** Prefer hosted config.json (Frontend stack); fall back to Vite env for local dev. */
export async function resolveAppConfig(): Promise<AppConfig> {
  // Explicit local mode wins before config.json (CloudFront should not set local).
  const envMode = stackModeFrom(import.meta.env.VITE_STACK_MODE as string | undefined);
  if (envMode === "local") {
    const envCfg = fromEnv();
    if (envCfg) return envCfg;
  }
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
    "Missing app config. For cost-free local UI: set VITE_STACK_MODE=local " +
      "(see web/.env.local.example) and run npm run local:containers:start-all. " +
      "For AWS: copy web/.env.example → web/.env.local with Cognito/Stream Outputs.",
  );
}

export function getAppConfig(): AppConfig {
  const envCfg = fromEnv();
  if (!envCfg) {
    throw new Error(
      "Missing VITE_* env. See web/.env.local.example (local) or .env.example (aws).",
    );
  }
  return envCfg;
}
