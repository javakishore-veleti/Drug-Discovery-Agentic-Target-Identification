#!/usr/bin/env node
/**
 * Story 5.4 — same auth+stream path the UI uses (Cognito IdP → SigV4 → Stream).
 * Proves mechanism → cardiotoxicity follow-up without restating drug name.
 *
 * Loads web/.env.local (or process env). Requires SMOKE_USER_EMAIL / SMOKE_USER_PASSWORD.
 */
import { readFileSync, existsSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import {
  CognitoIdentityProviderClient,
  InitiateAuthCommand,
} from "@aws-sdk/client-cognito-identity-provider";
import {
  CognitoIdentityClient,
  GetIdCommand,
  GetCredentialsForIdentityCommand,
} from "@aws-sdk/client-cognito-identity";
import { SignatureV4 } from "@aws-sdk/signature-v4";
import { Sha256 } from "@aws-crypto/sha256-js";
import { HttpRequest } from "@aws-sdk/protocol-http";

const __dir = dirname(fileURLToPath(import.meta.url));
const root = resolve(__dir, "..");

function loadEnvLocal() {
  const p = resolve(root, ".env.local");
  if (!existsSync(p)) return;
  for (const line of readFileSync(p, "utf8").split("\n")) {
    const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/);
    if (!m) continue;
    const key = m[1];
    let val = m[2].replace(/^['"]|['"]$/g, "");
    if (!process.env[key]) process.env[key] = val;
  }
}

loadEnvLocal();

function req(name) {
  const v = (process.env[name] || "").trim();
  if (!v) throw new Error(`Set ${name}`);
  return v;
}

function parseSse(body) {
  const events = [];
  for (const block of body.split("\n\n")) {
    for (const line of block.split("\n")) {
      if (!line.startsWith("data:")) continue;
      const raw = line.slice(5).trim();
      if (raw) events.push(JSON.parse(raw));
    }
  }
  return events;
}

async function sigv4Post(url, region, creds, payload) {
  const parsed = new URL(url);
  const body = JSON.stringify(payload);
  const request = new HttpRequest({
    protocol: parsed.protocol,
    hostname: parsed.hostname,
    method: "POST",
    path: parsed.pathname || "/",
    headers: { host: parsed.host, "content-type": "application/json" },
    body,
  });
  const signer = new SignatureV4({
    credentials: creds,
    region,
    service: "lambda",
    sha256: Sha256,
  });
  const signed = await signer.sign(request);
  const resp = await fetch(url, {
    method: signed.method,
    headers: signed.headers,
    body,
    signal: AbortSignal.timeout(300_000),
  });
  const text = await resp.text();
  return { status: resp.status, text, events: parseSse(text) };
}

const TURN1 = "What is the mechanism of action of Herceptin?";
const TURN2 =
  "Which patient populations are most vulnerable to its cardiotoxicity?";

async function main() {
  const region = process.env.VITE_AWS_REGION || process.env.AWS_REGION || "us-east-1";
  const streamUrl = req("VITE_STREAM_URL");
  const userPoolId = req("VITE_USER_POOL_ID");
  const clientId = req("VITE_USER_POOL_CLIENT_ID");
  const identityPoolId = req("VITE_IDENTITY_POOL_ID");
  const email = req("SMOKE_USER_EMAIL");
  const password = req("SMOKE_USER_PASSWORD");

  const idp = new CognitoIdentityProviderClient({ region });
  const auth = await idp.send(
    new InitiateAuthCommand({
      ClientId: clientId,
      AuthFlow: "USER_PASSWORD_AUTH",
      AuthParameters: { USERNAME: email, PASSWORD: password },
    }),
  );
  const idToken = auth.AuthenticationResult?.IdToken;
  if (!idToken) throw new Error("No IdToken");

  const cid = new CognitoIdentityClient({ region });
  const loginKey = `cognito-idp.${region}.amazonaws.com/${userPoolId}`;
  const { IdentityId } = await cid.send(
    new GetIdCommand({
      IdentityPoolId: identityPoolId,
      Logins: { [loginKey]: idToken },
    }),
  );
  const { Credentials } = await cid.send(
    new GetCredentialsForIdentityCommand({
      IdentityId,
      Logins: { [loginKey]: idToken },
    }),
  );
  const creds = {
    accessKeyId: Credentials.AccessKeyId,
    secretAccessKey: Credentials.SecretKey,
    sessionToken: Credentials.SessionToken,
  };

  const t1 = await sigv4Post(streamUrl, region, creds, { message: TURN1 });
  if (t1.status !== 200) throw new Error(`turn1 HTTP ${t1.status}`);
  const types1 = t1.events.map((e) => e.type);
  if (!types1.includes("tool_use")) throw new Error(`turn1 missing tool_use: ${types1}`);
  if (!types1.includes("done")) throw new Error("turn1 missing done");
  const sessionId = t1.events.find((e) => e.type === "session_started")?.sessionId;
  if (!sessionId) throw new Error("missing sessionId");
  const answer1 = t1.events
    .filter((e) => e.type === "token")
    .map((e) => e.text || "")
    .join("");
  if (!/\bPMID\b/i.test(answer1) && !t1.events.some((e) => e.type === "tool_result" && e.ids?.pmid?.length)) {
    console.warn("WARN: no PMID in turn1 answer/tool_result (tools may have returned empty)");
  }

  const t2 = await sigv4Post(streamUrl, region, creds, {
    message: TURN2,
    sessionId,
  });
  if (t2.status !== 200) throw new Error(`turn2 HTTP ${t2.status}`);
  const answer2 = t2.events
    .filter((e) => e.type === "token")
    .map((e) => e.text || "")
    .join("");
  if (!/\b(herceptin|trastuzumab|her2|erbb2|anti[- ]?her2)\b/i.test(answer2)) {
    throw new Error("turn2 lost Herceptin/HER2 context");
  }

  console.log(
    JSON.stringify(
      {
        ok: true,
        story: "5.4",
        path: "cognito_identity_pool_sigv4_stream",
        sessionId,
        turn1_types: types1,
        turn2_has_her2_context: true,
        answer2_preview: answer2.slice(0, 240),
      },
      null,
      2,
    ),
  );
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
