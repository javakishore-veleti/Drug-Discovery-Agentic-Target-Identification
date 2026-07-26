#!/usr/bin/env python3
"""
Story 4.2 — admin-provision a Cognito user (AD-10; no self-signup UI).

  export USER_POOL_ID=...
  export SMOKE_USER_EMAIL=asha@example.com
  export SMOKE_USER_PASSWORD='ChangeMe-Demo12'
  python stream/scripts/create_cognito_user.py
"""

from __future__ import annotations

import os
import sys

import boto3
from botocore.exceptions import ClientError


def main() -> int:
    pool = (os.environ.get("USER_POOL_ID") or "").strip()
    email = (os.environ.get("SMOKE_USER_EMAIL") or "").strip()
    password = os.environ.get("SMOKE_USER_PASSWORD") or ""
    region = (
        os.environ.get("AWS_REGION")
        or os.environ.get("AWS_DEFAULT_REGION")
        or "us-east-1"
    )
    if not pool or not email or not password:
        print(
            "Set USER_POOL_ID, SMOKE_USER_EMAIL, SMOKE_USER_PASSWORD",
            file=sys.stderr,
        )
        return 2
    if len(password) < 12:
        print("Password must be at least 12 characters (pool policy)", file=sys.stderr)
        return 2

    client = boto3.client("cognito-idp", region_name=region)
    try:
        client.admin_create_user(
            UserPoolId=pool,
            Username=email,
            UserAttributes=[
                {"Name": "email", "Value": email},
                {"Name": "email_verified", "Value": "true"},
            ],
            MessageAction="SUPPRESS",
        )
        print(f"created user={email}", file=sys.stderr)
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "")
        if code != "UsernameExistsException":
            raise
        print(f"user exists={email}", file=sys.stderr)

    client.admin_set_user_password(
        UserPoolId=pool,
        Username=email,
        Password=password,
        Permanent=True,
    )
    print("password set (permanent)", file=sys.stderr)
    print(email)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
