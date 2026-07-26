"""
ClinicalTrials.gov API v2 adapter.

Public API: https://clinicaltrials.gov/api/v2/studies
Return shape matches architecture AD-9 / AD-15 (shared with pubmed).
"""

from __future__ import annotations

import os
import re
import time
from typing import Any

import requests

TOOL_NAME = "clinicaltrials"
API_BASE = "https://clinicaltrials.gov/api/v2/studies"
DEFAULT_RETMAX = 8
DEFAULT_TIMEOUT_SECONDS = 45.0
MAX_RETRIES_ON_429 = 4
# CT.gov fronting rejects some Python urllib fingerprints; requests works.
USER_AGENT = (
    "AgenticTargetID/0.1 (+https://github.com/javakishore-veleti/"
    "Drug-Discovery-Agentic-Target-Identification; research)"
)
NCT_RE = re.compile(r"^NCT\d{8}$")


def _empty_ids() -> dict[str, list[str]]:
    return {"pmid": [], "nct": [], "chembl": []}


def _ok_result(
    *,
    ncts: list[str],
    summary: str,
    studies: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    return {
        "status": "ok",
        "tool": TOOL_NAME,
        "ids": {**_empty_ids(), "nct": ncts},
        "summary": summary,
        "studies": studies or [],
    }


def _error_result(message: str) -> dict[str, Any]:
    return {
        "status": "error",
        "tool": TOOL_NAME,
        "message": message,
        "ids": _empty_ids(),
        "summary": "",
        "studies": [],
    }


def _remaining(deadline: float) -> float:
    return max(0.0, deadline - time.monotonic())


def _normalize_nct(value: Any) -> str | None:
    nct = str(value or "").strip().upper()
    if NCT_RE.match(nct):
        return nct
    return None


def search_clinicaltrials(
    query: str,
    *,
    retmax: int = DEFAULT_RETMAX,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """
    Search ClinicalTrials.gov via API v2.

    Returns a normalized tool result:
      status: "ok" | "error"
      tool: "clinicaltrials"
      ids: { pmid: [], nct: string[], chembl: [] }
      summary: short text for the agent
      studies: [{nct, title, status}, ...] on success
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
        params = {
            "query.term": q,
            "pageSize": str(retmax),
            "format": "json",
        }
        # Build URL with requests params for correct encoding
        remaining = _remaining(deadline)
        if remaining <= 0:
            return _error_result("ClinicalTrials tool exceeded wall-clock timeout")

        attempt = 0
        payload: dict[str, Any] = {}
        while True:
            attempt += 1
            remaining = _remaining(deadline)
            if remaining <= 0:
                return _error_result("ClinicalTrials tool exceeded wall-clock timeout")
            try:
                resp = requests.get(
                    API_BASE,
                    params=params,
                    headers={
                        "User-Agent": USER_AGENT,
                        "Accept": "application/json",
                    },
                    timeout=min(remaining, 20.0),
                    verify=os.environ.get("CLINICALTRIALS_SSL_VERIFY", "true")
                    .strip()
                    .lower()
                    not in {"0", "false", "no", "off"},
                )
                if resp.status_code == 429 and attempt <= MAX_RETRIES_ON_429:
                    sleep_for = min(2 ** (attempt - 1), _remaining(deadline) - 0.05)
                    if sleep_for <= 0:
                        return _error_result(
                            "ClinicalTrials tool exceeded wall-clock timeout while backing off on HTTP 429"
                        )
                    time.sleep(sleep_for)
                    continue
                if resp.status_code >= 400:
                    return _error_result(
                        f"ClinicalTrials HTTP {resp.status_code}: {resp.reason}"
                    )
                payload = resp.json()
                break
            except requests.Timeout:
                return _error_result("ClinicalTrials tool exceeded wall-clock timeout")
            except requests.RequestException as exc:
                return _error_result(f"ClinicalTrials network error: {exc.__class__.__name__}")

        studies_out: list[dict[str, str]] = []
        ncts: list[str] = []
        for study in payload.get("studies") or []:
            if not isinstance(study, dict):
                continue
            proto = study.get("protocolSection") or {}
            ident = proto.get("identificationModule") or {}
            status_mod = proto.get("statusModule") or {}
            nct = _normalize_nct(ident.get("nctId"))
            if not nct:
                continue
            title = str(ident.get("briefTitle") or "").strip()
            status = str(status_mod.get("overallStatus") or "").strip()
            ncts.append(nct)
            studies_out.append({"nct": nct, "title": title, "status": status})

        if ncts:
            lines = [
                f"{s['nct']}"
                + (f" [{s['status']}]" if s.get("status") else "")
                + (f": {s['title']}" if s.get("title") else "")
                for s in studies_out[:retmax]
            ]
            summary = f"Found {len(ncts)} ClinicalTrials.gov hit(s) for query.\n" + "\n".join(
                lines
            )
        else:
            summary = f"No ClinicalTrials.gov hits for query: {q}"

        return _ok_result(ncts=ncts, summary=summary, studies=studies_out)

    except TimeoutError as exc:
        return _error_result(str(exc) or "ClinicalTrials tool timed out")
    except Exception as exc:  # noqa: BLE001 — tool boundary must always return shaped error
        return _error_result(f"ClinicalTrials unexpected error: {exc.__class__.__name__}")
