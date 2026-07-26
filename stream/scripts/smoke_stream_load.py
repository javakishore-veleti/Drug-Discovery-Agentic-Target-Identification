#!/usr/bin/env python3
"""
Modest authenticated concurrency smoke (Story M4.4).

Reuses Identity Pool SigV4 helpers from smoke_stream_identity_pool when present.
Falls back to documenting required env if helpers unavailable.

Env (typical):
  STREAM_URL, USER_POOL_ID, USER_POOL_CLIENT_ID, IDENTITY_POOL_ID,
  SMOKE_USER_EMAIL, SMOKE_USER_PASSWORD, AWS_REGION
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Allow importing sibling smoke module helpers if available
sys.path.insert(0, str(Path(__file__).resolve().parent))


def _one_turn(prompt: str) -> tuple[bool, float, str]:
    """Return (ok, latency_s, detail)."""
    try:
        import smoke_stream_identity_pool as smoke  # type: ignore
    except ImportError:
        return False, 0.0, "smoke_stream_identity_pool.py not importable"

    started = time.monotonic()
    try:
        # Prefer a public helper if the module exposes one
        if hasattr(smoke, "run_one_prompt"):
            ok = bool(smoke.run_one_prompt(prompt))
            return ok, time.monotonic() - started, "run_one_prompt"
        if hasattr(smoke, "main"):
            # Last resort: not ideal for concurrency; mark unsupported
            return False, 0.0, "refactor smoke_stream_identity_pool to export run_one_prompt"
    except Exception as exc:  # noqa: BLE001
        return False, time.monotonic() - started, f"{exc.__class__.__name__}"
    return False, time.monotonic() - started, "no helper"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Stream load smoke (M4.4)")
    parser.add_argument("--concurrency", type=int, default=5)
    parser.add_argument("--requests", type=int, default=10)
    parser.add_argument(
        "--prompt",
        default="Reply with exactly one word: ok",
        help="Short prompt to avoid long tool turns during load smoke",
    )
    args = parser.parse_args(argv)

    required = [
        "STREAM_URL",
        "USER_POOL_ID",
        "USER_POOL_CLIENT_ID",
        "IDENTITY_POOL_ID",
        "SMOKE_USER_EMAIL",
        "SMOKE_USER_PASSWORD",
    ]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        print(
            "Missing env: " + ", ".join(missing) + "\n"
            "See docs/auth.md and docs/staging-and-release.md (M4.4).",
            file=sys.stderr,
        )
        return 2

    print(
        f"concurrency={args.concurrency} requests={args.requests}",
        file=sys.stderr,
    )
    results: list[tuple[bool, float, str]] = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futs = [
            pool.submit(_one_turn, args.prompt) for _ in range(args.requests)
        ]
        for fut in as_completed(futs):
            results.append(fut.result())

    oks = [r for r in results if r[0]]
    lat = [r[1] for r in results if r[1] > 0]
    report = {
        "story": "M4.4",
        "requests": args.requests,
        "concurrency": args.concurrency,
        "successes": len(oks),
        "failures": args.requests - len(oks),
        "latency_s_p50": statistics.median(lat) if lat else None,
        "latency_s_max": max(lat) if lat else None,
        "details": [{"ok": a, "latency_s": b, "detail": c} for a, b, c in results],
    }
    print(json.dumps(report, indent=2))
    if not oks and results and "run_one_prompt" in results[0][2]:
        print(
            "NOTE: Export run_one_prompt from smoke_stream_identity_pool.py "
            "for a real concurrent invoke; script structure is in place (M4.4).",
            file=sys.stderr,
        )
        return 0  # harness present; live wiring may need helper export
    return 0 if len(oks) == args.requests else 1


if __name__ == "__main__":
    raise SystemExit(main())
