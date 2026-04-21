"""Scorecard module: compute a health score for a vault based on various checks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from envault.storage import load_vault, get_vault_path
from envault.lint import lint_vault
from envault.checksums import verify_checksum
from envault.expiry import get_expiry, is_expired
from envault.ttl import is_expired as ttl_is_expired


def _get_scorecard_path(vault_path: Path) -> Path:
    return vault_path.parent / "scorecards.json"


def _load_scorecards(vault_path: Path) -> dict[str, Any]:
    p = _get_scorecard_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_scorecards(vault_path: Path, data: dict[str, Any]) -> None:
    p = _get_scorecard_path(vault_path)
    p.write_text(json.dumps(data, indent=2))


def compute_score(vault_path: Path, password: str) -> dict[str, Any]:
    """Compute a health score (0-100) for the vault and return a detailed report."""
    vault = load_vault(vault_path, password)
    keys = list(vault.keys())
    total = len(keys)

    if total == 0:
        return {"score": 100, "total_keys": 0, "issues": [], "breakdown": {}}

    lint_result = lint_vault(vault_path, password)
    lint_penalty = len(lint_result.errors) * 5 + len(lint_result.warnings) * 2

    expired_count = 0
    for key in keys:
        exp = get_expiry(vault_path, key)
        if exp and is_expired(vault_path, key):
            expired_count += 1
        elif ttl_is_expired(vault_path, key):
            expired_count += 1

    checksum_failures = 0
    for key, value in vault.items():
        if not verify_checksum(vault_path, key, value):
            checksum_failures += 1

    expired_penalty = int((expired_count / total) * 30)
    checksum_penalty = int((checksum_failures / total) * 25)

    raw = 100 - min(lint_penalty, 30) - expired_penalty - checksum_penalty
    score = max(0, min(100, raw))

    report = {
        "score": score,
        "total_keys": total,
        "issues": [str(i) for i in lint_result.errors + lint_result.warnings],
        "breakdown": {
            "lint_penalty": min(lint_penalty, 30),
            "expired_penalty": expired_penalty,
            "checksum_penalty": checksum_penalty,
            "expired_keys": expired_count,
            "checksum_failures": checksum_failures,
        },
    }

    data = _load_scorecards(vault_path)
    data["latest"] = report
    _save_scorecards(vault_path, data)
    return report


def get_latest_scorecard(vault_path: Path) -> dict[str, Any] | None:
    data = _load_scorecards(vault_path)
    return data.get("latest")
