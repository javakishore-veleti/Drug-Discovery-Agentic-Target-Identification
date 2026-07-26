import { fetchAuthSession } from "aws-amplify/auth";
import { Sha256 } from "@aws-crypto/sha256-js";
import { HttpRequest } from "@aws-sdk/protocol-http";
import { SignatureV4 } from "@aws-sdk/signature-v4";

/**
 * POST to the IAM Function URL with Cognito Identity Pool temporary credentials
 * (AD-1). Never uses AgentCore Runtime IAM from the browser.
 */
export async function sigv4Post(
  url: string,
  region: string,
  body: unknown,
  signal?: AbortSignal,
): Promise<Response> {
  const session = await fetchAuthSession();
  const credentials = session.credentials;
  if (!credentials?.accessKeyId || !credentials.secretAccessKey) {
    throw new Error("Not signed in — no Identity Pool credentials");
  }

  const parsed = new URL(url);
  const payload = JSON.stringify(body);
  const request = new HttpRequest({
    protocol: parsed.protocol,
    hostname: parsed.hostname,
    port: parsed.port ? Number(parsed.port) : undefined,
    method: "POST",
    path: parsed.pathname || "/",
    headers: {
      host: parsed.host,
      "content-type": "application/json",
    },
    body: payload,
  });

  const signer = new SignatureV4({
    credentials: {
      accessKeyId: credentials.accessKeyId,
      secretAccessKey: credentials.secretAccessKey,
      sessionToken: credentials.sessionToken,
    },
    region,
    service: "lambda",
    sha256: Sha256,
  });

  const signed = await signer.sign(request);
  return fetch(url, {
    method: signed.method,
    headers: signed.headers as HeadersInit,
    body: payload,
    signal,
  });
}
