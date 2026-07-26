#!/usr/bin/env python3
"""
Story 4.2 — Cognito User Pool → Identity Pool → SigV4 Stream Function URL.

Proves:
  - authenticated IdP temporary credentials can call StreamUrl
  - unsigned / unauthenticated request is rejected

Does NOT use AgentCore Runtime IAM (AD-1).

Env:
  STREAM_URL, USER_POOL_ID, USER_POOL_CLIENT_ID, IDENTITY_POOL_ID
  SMOKE_USER_EMAIL, SMOKE_USER_PASSWORD
"""

from __future__ import annotations

import json
import os
import ssl
import sys
from urllib import error, request

import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials

try:
    import certifi

    _SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except Exception:  # noqa: BLE001
    _SSL_CONTEXT = ssl.create_default_context()


def _parse_sse(body: str) -> list[dict]:
    events: list[dict] = []
    for block in body.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        for line in block.splitlines():
            if line.startswith("data:"):
                raw = line[5:].strip()
                if raw:
                    events.append(json.loads(raw))
    return events


def _require(name: str) -> str:
    val = (os.environ.get(name) or "").strip()
    if not val:
        raise SystemExit(f"Set {name}")
    return val


def _id_token(region: str, client_id: str, email: str, password: str) -> str:
    idp = boto3.client("cognito-idp", region_name=region)
    resp = idp.initiate_auth(
        ClientId=client_id,
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": email, "PASSWORD": password},
    )
    token = (resp.get("AuthenticationResult") or {}).get("IdToken")
    if not token:
        raise RuntimeError(f"No IdToken in InitiateAuth: {list(resp.keys())}")
    return token


def _temp_creds(
    region: str,
    identity_pool_id: str,
    user_pool_id: str,
    id_token: str,
) -> Credentials:
    cid = boto3.client("cognito-identity", region_name=region)
    login_key = f"cognito-idp.{region}.amazonaws.com/{user_pool_id}"
    identity = cid.get_id(
        IdentityPoolId=identity_pool_id,
        Logins={login_key: id_token},
    )
    creds = cid.get_credentials_for_identity(
        IdentityId=identity["IdentityId"],
        Logins={login_key: id_token},
    )["Credentials"]
    return Credentials(
        access_key=creds["AccessKeyId"],
        secret_key=creds["SecretKey"],
        token=creds["SessionToken"],
    )


def _post(url: str, data: bytes, headers: dict[str, str]) -> tuple[int, str]:
    req = request.Request(url, data=data, headers=headers, method="POST")
    try:
        with request.urlopen(req, timeout=300, context=_SSL_CONTEXT) as resp:
            return resp.status, resp.read().decode("utf-8")
    except error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")


def main() -> int:
    stream_url = _require("STREAM_URL")
    user_pool_id = _require("USER_POOL_ID")
    client_id = _require("USER_POOL_CLIENT_ID")
    identity_pool_id = _require("IDENTITY_POOL_ID")
    email = _require("SMOKE_USER_EMAIL")
    password = _require("SMOKE_USER_PASSWORD")
    region = (
        os.environ.get("AWS_REGION")
        or os.environ.get("AWS_DEFAULT_REGION")
        or "us-east-1"
    )
    message = " ".join(sys.argv[1:]).strip() or "Reply with exactly one word: ok"
    payload = json.dumps({"message": message}).encode("utf-8")

    print(f"stream_url={stream_url}", file=sys.stderr)
    print("auth=Cognito Identity Pool → SigV4 (not Runtime IAM)", file=sys.stderr)

    # --- unsigned must fail ---
    unsigned_status, unsigned_body = _post(
        stream_url,
        payload,
        {"Content-Type": "application/json"},
    )
    print(f"unsigned_status={unsigned_status}", file=sys.stderr)
    if unsigned_status in (200, 201, 204):
        print("FAIL: unsigned request was accepted", file=sys.stderr)
        print(unsigned_body[:500], file=sys.stderr)
        return 1
    if unsigned_status not in (401, 403):
        print(
            f"WARN: expected 401/403 for unsigned, got {unsigned_status}",
            file=sys.stderr,
        )

    # --- authenticated IdP SigV4 must succeed ---
    id_token = _id_token(region, client_id, email, password)
    creds = _temp_creds(region, identity_pool_id, user_pool_id, id_token)
    aws_req = AWSRequest(
        method="POST",
        url=stream_url,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    SigV4Auth(creds, "lambda", region).add_auth(aws_req)
    prepared = aws_req.prepare()
    status, body = _post(stream_url, payload, dict(prepared.headers))
    print(body)
    print(f"signed_status={status}", file=sys.stderr)
    if status != 200:
        print("FAIL: signed Identity Pool request rejected", file=sys.stderr)
        return 1

    events = _parse_sse(body)
    types = [e.get("type") for e in events]
    if not events or events[0].get("type") != "session_started":
        print("FAIL: missing session_started", file=sys.stderr)
        return 1
    if events[-1].get("type") != "done":
        print("FAIL: missing done", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "ok": True,
                "unsigned_status": unsigned_status,
                "signed_status": status,
                "sessionId": events[0].get("sessionId"),
                "types": types,
                "auth": "cognito_identity_pool_sigv4",
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
