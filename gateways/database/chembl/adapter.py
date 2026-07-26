"""
ChEMBL Data Web Services adapter.

Public API: https://www.ebi.ac.uk/chembl/api/data/molecule/search.json
Return shape matches architecture AD-9 / AD-15 (shared with pubmed / clinicaltrials).
"""

from __future__ import annotations

import os
import re
import time
from typing import Any

import requests

TOOL_NAME = "chembl"
API_BASE = "https://www.ebi.ac.uk/chembl/api/data/molecule/search.json"
DEFAULT_RETMAX = 8
DEFAULT_TIMEOUT_SECONDS = 45.0
MAX_RETRIES_ON_429 = 4
USER_AGENT = (
    "AgenticTargetID/0.1 (+https://github.com/javakishore-veleti/"
    "Drug-Discovery-Agentic-Target-Identification; research)"
)
CHEMBL_RE = re.compile(r"^CHEMBL\d+$")


def _empty_ids() -> dict[str, list[str]]:
    return {"pmid": [], "nct": [], "chembl": []}


def _ok_result(
    *,
    chembl_ids: list[str],
    summary: str,
    molecules: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    return {
        "status": "ok",
        "tool": TOOL_NAME,
        "ids": {**_empty_ids(), "chembl": chembl_ids},
        "summary": summary,
        "molecules": molecules or [],
    }


def _error_result(message: str) -> dict[str, Any]:
    return {
        "status": "error",
        "tool": TOOL_NAME,
        "message": message,
        "ids": _empty_ids(),
        "summary": "",
        "molecules": [],
    }


def _remaining(deadline: float) -> float:
    return max(0.0, deadline - time.monotonic())


def _ssl_verify() -> bool:
    return (
        os.environ.get("CHEMBL_SSL_VERIFY", "true").strip().lower()
        not in {"0", "false", "no", "off"}
    )


def _normalize_chembl(value: Any) -> str | None:
    cid = str(value or "").strip().upper()
    if CHEMBL_RE.match(cid):
        return cid
    return None


def search_chembl(
    query: str,
    *,
    retmax: int = DEFAULT_RETMAX,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """
    Search ChEMBL molecules via the public search endpoint.

    Returns a normalized tool result:
      status: "ok" | "error"
      tool: "chembl"
      ids: { pmid: [], nct: [], chembl: string[] }
      summary: short text for the agent
      molecules: [{chembl, name, molecule_type}, ...] on success
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
        params = {"q": q, "limit": str(retmax)}
        attempt = 0
        payload: dict[str, Any] = {}
        while True:
            attempt += 1
            remaining = _remaining(deadline)
            if remaining <= 0:
                return _error_result("ChEMBL tool exceeded wall-clock timeout")
            try:
                resp = requests.get(
                    API_BASE,
                    params=params,
                    headers={
                        "User-Agent": USER_AGENT,
                        "Accept": "application/json",
                    },
                    timeout=min(remaining, 20.0),
                    verify=_ssl_verify(),
                )
                if resp.status_code == 429 and attempt <= MAX_RETRIES_ON_429:
                    sleep_for = min(2 ** (attempt - 1), _remaining(deadline) - 0.05)
                    if sleep_for <= 0:
                        return _error_result(
                            "ChEMBL tool exceeded wall-clock timeout while backing off on HTTP 429"
                        )
                    time.sleep(sleep_for)
                    continue
                if resp.status_code >= 400:
                    return _error_result(
                        f"ChEMBL HTTP {resp.status_code}: {resp.reason}"
                    )
                payload = resp.json()
                break
            except requests.Timeout:
                return _error_result("ChEMBL tool exceeded wall-clock timeout")
            except requests.RequestException:
                return _error_result("ChEMBL network error: RequestException")

        molecules_out: list[dict[str, str]] = []
        chembl_ids: list[str] = []
        seen: set[str] = set()
        for mol in payload.get("molecules") or []:
            if not isinstance(mol, dict):
                continue
            cid = _normalize_chembl(mol.get("molecule_chembl_id"))
            if not cid or cid in seen:
                continue
            seen.add(cid)
            name = str(mol.get("pref_name") or "").strip()
            mol_type = str(mol.get("molecule_type") or "").strip()
            chembl_ids.append(cid)
            molecules_out.append(
                {"chembl": cid, "name": name, "molecule_type": mol_type}
            )

        if chembl_ids:
            lines = [
                f"{m['chembl']}"
                + (f" ({m['molecule_type']})" if m.get("molecule_type") else "")
                + (f": {m['name']}" if m.get("name") else "")
                for m in molecules_out[:retmax]
            ]
            summary = f"Found {len(chembl_ids)} ChEMBL hit(s) for query.\n" + "\n".join(
                lines
            )
        else:
            summary = f"No ChEMBL hits for query: {q}"

        return _ok_result(
            chembl_ids=chembl_ids, summary=summary, molecules=molecules_out
        )

    except TimeoutError as exc:
        return _error_result(str(exc) or "ChEMBL tool timed out")
    except Exception as exc:  # noqa: BLE001 — tool boundary must always return shaped error
        return _error_result(f"ChEMBL unexpected error: {exc.__class__.__name__}")
