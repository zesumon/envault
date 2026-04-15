"""Lint/validate secrets in the vault against simple rules."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from envault.storage import load_vault, get_secret


@dataclass
class LintIssue:
    key: str
    severity: str  # "error" | "warning"
    message: str


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


_KEY_RE = re.compile(r'^[A-Z][A-Z0-9_]*$')
_WEAK_VALUES = {"", "changeme", "secret", "password", "1234", "test"}


def _check_key_naming(key: str) -> Optional[LintIssue]:
    if not _KEY_RE.match(key):
        return LintIssue(
            key=key,
            severity="warning",
            message=f"Key '{key}' does not follow UPPER_SNAKE_CASE convention",
        )
    return None


def _check_empty_value(key: str, value: str) -> Optional[LintIssue]:
    if value.strip() == "":
        return LintIssue(key=key, severity="error", message=f"Key '{key}' has an empty value")
    return None


def _check_weak_value(key: str, value: str) -> Optional[LintIssue]:
    if value.strip().lower() in _WEAK_VALUES:
        return LintIssue(
            key=key,
            severity="warning",
            message=f"Key '{key}' appears to have a weak/placeholder value",
        )
    return None


def lint_vault(vault_path: str, password: str) -> LintResult:
    """Run all lint checks against every secret in the vault."""
    result = LintResult()
    vault = load_vault(vault_path, password)
    secrets: dict = vault.get("secrets", {})

    for key in sorted(secrets.keys()):
        value = get_secret(vault_path, password, key) or ""
        for checker in (_check_key_naming, _check_empty_value, _check_weak_value):
            issue = checker(key, value)
            if issue:
                result.issues.append(issue)

    return result
