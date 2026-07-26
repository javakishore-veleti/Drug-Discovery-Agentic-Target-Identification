"""
Open Targets Platform adapter (Story M3.3) — public GraphQL API.

https://api.platform.opentargets.org/api/v4/graphql
Return shape matches AD-9 / AD-15 (ids.ensembl for target hits).
"""

from __future__ import annotations

import json
import os
import ssl
import time
import urllib.error
import urllib.request
from typing import Any

TOOL_NAME = "opentargets"
GRAPHQL_URL = "https://api.platform.opentargets.org/api/v4/graphql"
DEFAULT_RETMAX = 8
DEFAULT_TIMEOUT_SECONDS = 45.0
MAX_RETRIES_ON_429 = 4
USER_AGENT = "AgenticTargetID/0.1 (research; mailto:none)"

_SEARCH_QUERY = """
query Search($queryString: String!, $entityNames: [String!], $page: Pagination!) {
  search(queryString: $queryString, entityNames: $entityNames, page: $page) {
    total
    hits {
      id
      entity
      name
      description
      score
    }
  }
}
"""


def _ssl_context() -> ssl.SSLContext:
    verify = os.environ.get("OPENTARGETS_SSL_VERIFY", "true").strip().lower()
    if verify in {"0", "false", "no", "off"}:
        return ssl._create_unverified_context()  # noqa: S323
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def _empty_ids() -> dict[str, list[str]]:
    return {"pmid": [], "nct": [], "chembl": [], "ensembl": []}


def _ok_result(
    *,
    ensembl_ids: list[str],
    summary: str,
    hits: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "status": "ok",
        "tool": TOOL_NAME,
        "ids": {**_empty_ids(), "ensembl": ensembl_ids},
        "summary": summary,
        "hits": hits or [],
    }


def _error_result(message: str) -> dict[str, Any]:
    return {
        "status": "error",
        "tool": TOOL_NAME,
        "message": message,
        "ids": _empty_ids(),
        "summary": "",
        "hits": [],
    }


def _remaining(deadline: float) -> float:
    return max(0.0, deadline - time.monotonic())


def _http_post_json(payload: dict[str, Any], *, deadline: float) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    last_err: Exception | None = None
    for attempt in range(MAX_RETRIES_ON_429 + 1):
        rem = _remaining(deadline)
        if rem <= 0:
            raise TimeoutError("Open Targets wall-clock budget exceeded")
        req = urllib.request.Request(
            GRAPHQL_URL,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": USER_AGENT,
            },
        )
        try:
            with urllib.request.urlopen(
                req, timeout=min(30.0, rem), context=_ssl_context()
            ) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            last_err = exc
            if exc.code == 429 and attempt < MAX_RETRIES_ON_429:
                time.sleep(min(2**attempt, _remaining(deadline)))
                continue
            raise
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_err = exc
            raise
    raise RuntimeError(f"Open Targets request failed: {last_err}")


def search_opentargets(query: str, retmax: int = DEFAULT_RETMAX) -> dict[str, Any]:
    """
    Search Open Targets (prefer targets). Returns ensembl gene IDs when present.
    """
    q = (query or "").strip()
    if not q:
        return _error_result("query is required")
    try:
        n = int(retmax)
    except (TypeError, ValueError):
        n = DEFAULT_RETMAX
    n = max(1, min(20, n))

    deadline = time.monotonic() + DEFAULT_TIMEOUT_SECONDS
    try:
        data = _http_post_json(
            {
                "query": _SEARCH_QUERY,
                "variables": {
                    "queryString": q,
                    "entityNames": ["target"],
                    "page": {"index": 0, "size": n},
                },
            },
            deadline=deadline,
        )
    except Exception as exc:  # noqa: BLE001 — map to safe tool_result
        return _error_result(f"Open Targets request failed: {exc.__class__.__name__}")

    if data.get("errors"):
        # Safe short message — no raw stack / secrets
        return _error_result("Open Targets GraphQL returned errors")

    search = (data.get("data") or {}).get("search") or {}
    hits_raw = search.get("hits") or []
    hits: list[dict[str, Any]] = []
    ensembl: list[str] = []
    for h in hits_raw:
        if not isinstance(h, dict):
            continue
        hid = str(h.get("id") or "").strip()
        entity = str(h.get("entity") or "")
        name = str(h.get("name") or "")
        desc = str(h.get("description") or "")[:300]
        hits.append(
            {
                "id": hid,
                "entity": entity,
                "name": name,
                "description": desc,
            }
        )
        if hid.startswith("ENSG"):
            ensembl.append(hid)

    ensembl = sorted(set(ensembl))
    total = search.get("total")
    summary = (
        f"Open Targets search for {q!r}: {len(hits)} hits"
        + (f" (total≈{total})" if total is not None else "")
        + (f"; ensembl={', '.join(ensembl[:5])}" if ensembl else "; no ENSG ids")
    )
    return _ok_result(ensembl_ids=ensembl, summary=summary, hits=hits)
