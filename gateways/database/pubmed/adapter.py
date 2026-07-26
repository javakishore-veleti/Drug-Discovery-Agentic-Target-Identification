"""
PubMed / NCBI E-utilities adapter.

Public API only (https://www.ncbi.nlm.nih.gov/books/NBK25499/).
Return shape matches architecture AD-9 / AD-15 for reuse by Gateway Lambdas.
"""

from __future__ import annotations

import json
import os
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

TOOL_NAME = "pubmed"
EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
DEFAULT_RETMAX = 8
# AD-15: soft per-tool wall-clock budget
DEFAULT_TIMEOUT_SECONDS = 45.0
MAX_RETRIES_ON_429 = 4
USER_AGENT = "AgenticTargetID/0.1 (research; mailto:none)"


def _ssl_context() -> ssl.SSLContext | None:
    """
    TLS context for NCBI HTTPS.

    Uses certifi CA bundle when available. Set PUBMED_SSL_VERIFY=false only for
    local troubleshooting behind intercepting proxies (not for production).
    """
    verify = os.environ.get("PUBMED_SSL_VERIFY", "true").strip().lower()
    if verify in {"0", "false", "no", "off"}:
        return ssl._create_unverified_context()  # noqa: S323 — explicit opt-out
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def _empty_ids() -> dict[str, list[str]]:
    return {"pmid": [], "nct": [], "chembl": []}


def _ok_result(
    *,
    pmids: list[str],
    summary: str,
    articles: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    return {
        "status": "ok",
        "tool": TOOL_NAME,
        "ids": {**_empty_ids(), "pmid": pmids},
        "summary": summary,
        "articles": articles or [],
    }


def _error_result(message: str) -> dict[str, Any]:
    return {
        "status": "error",
        "tool": TOOL_NAME,
        "message": message,
        "ids": _empty_ids(),
        "summary": "",
        "articles": [],
    }


def _remaining(deadline: float) -> float:
    return max(0.0, deadline - time.monotonic())


def _http_get_json(url: str, *, deadline: float) -> dict[str, Any]:
    remaining = _remaining(deadline)
    if remaining <= 0:
        raise TimeoutError("PubMed tool exceeded wall-clock timeout")

    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        method="GET",
    )
    # Cap individual socket wait so we never exceed the tool budget by much
    socket_timeout = min(remaining, 20.0)
    attempt = 0
    while True:
        attempt += 1
        remaining = _remaining(deadline)
        if remaining <= 0:
            raise TimeoutError("PubMed tool exceeded wall-clock timeout")
        socket_timeout = min(remaining, 20.0)
        try:
            with urllib.request.urlopen(
                req,
                timeout=socket_timeout,
                context=_ssl_context(),
            ) as resp:
                raw = resp.read().decode("utf-8")
            return json.loads(raw)
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt <= MAX_RETRIES_ON_429:
                # Exponential backoff; still respect deadline
                sleep_for = min(2 ** (attempt - 1), _remaining(deadline) - 0.05)
                if sleep_for <= 0:
                    raise TimeoutError(
                        "PubMed tool exceeded wall-clock timeout while backing off on HTTP 429"
                    ) from exc
                time.sleep(sleep_for)
                continue
            raise


def search_pubmed(
    query: str,
    *,
    retmax: int = DEFAULT_RETMAX,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """
    Search PubMed via ESearch (+ ESummary for titles).

    Returns a normalized tool result:
      status: "ok" | "error"
      tool: "pubmed"
      ids: { pmid: string[], nct: [], chembl: [] }
      summary: short text for the agent
      articles: [{pmid, title}, ...] on success
      message: present on error
    """
    q = (query or "").strip()
    if not q:
        return _error_result("query must be a non-empty string")

    try:
        budget = float(timeout_seconds)
    except (TypeError, ValueError):
        return _error_result("timeout_seconds must be a number")
    if budget <= 0:
        return _error_result("timeout_seconds must be positive")
    deadline = time.monotonic() + budget
    retmax = max(1, min(int(retmax), 20))

    try:
        search_params = urllib.parse.urlencode(
            {
                "db": "pubmed",
                "term": q,
                "retmax": str(retmax),
                "retmode": "json",
                "sort": "relevance",
            }
        )
        search_url = f"{EUTILS_BASE}/esearch.fcgi?{search_params}"
        search_payload = _http_get_json(search_url, deadline=deadline)
        idlist = (
            search_payload.get("esearchresult", {}).get("idlist")
            or search_payload.get("esearchresult", {}).get("idList")
            or []
        )
        pmids = [str(x) for x in idlist if str(x).strip()]

        articles: list[dict[str, str]] = []
        if pmids and _remaining(deadline) > 0.5:
            sum_params = urllib.parse.urlencode(
                {
                    "db": "pubmed",
                    "id": ",".join(pmids),
                    "retmode": "json",
                }
            )
            sum_url = f"{EUTILS_BASE}/esummary.fcgi?{sum_params}"
            try:
                summary_payload = _http_get_json(sum_url, deadline=deadline)
                result_map = summary_payload.get("result", {})
                for pmid in pmids:
                    meta = result_map.get(pmid) or {}
                    title = str(meta.get("title") or "").strip()
                    articles.append({"pmid": pmid, "title": title})
            except Exception:
                # Titles are optional; IDs alone still satisfy AD-9
                articles = [{"pmid": p, "title": ""} for p in pmids]

        if not articles and pmids:
            articles = [{"pmid": p, "title": ""} for p in pmids]

        if pmids:
            lines = [
                f"PMID {a['pmid']}" + (f": {a['title']}" if a.get("title") else "")
                for a in articles[:retmax]
            ]
            summary = f"Found {len(pmids)} PubMed hit(s) for query.\n" + "\n".join(lines)
        else:
            summary = f"No PubMed hits for query: {q}"

        return _ok_result(pmids=pmids, summary=summary, articles=articles)

    except TimeoutError as exc:
        return _error_result(str(exc) or "PubMed tool timed out")
    except urllib.error.HTTPError as exc:
        return _error_result(f"PubMed HTTP {exc.code}: {exc.reason}")
    except urllib.error.URLError as exc:
        return _error_result(f"PubMed network error: {exc.reason!s}")
    except json.JSONDecodeError:
        return _error_result("PubMed returned invalid JSON")
    except Exception as exc:  # noqa: BLE001 — tool boundary must always return shaped error
        return _error_result(f"PubMed unexpected error: {exc.__class__.__name__}")
