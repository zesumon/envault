"""Compliance checks: verify vault keys meet naming and value policies."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from envault.storage import load_vault, get_vault_path
from envault.crypto import decrypt


_KEY_PATTERN = re.compile(r'^[A-Z][A-Z0-9_]*$')
_FORBIDDEN_PREFIXES = ("AWS_SECRET", "PRIVATE_KEY", "PASSWORD", "TOKEN")


@dataclass
class ComplianceIssue:
    key: str
    rule: str
    severity: str  # 'error' | 'warning'


@dataclass
class ComplianceReport:
    issues: List[ComplianceIssue] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)

    @property
    def errors(self) -> List[ComplianceIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[ComplianceIssue]:
        return [i for i in self.issues if i.severity == "warning"]


def _check_key_naming(key: str) -> List[ComplianceIssue]:
    issues: List[ComplianceIssue] = []
    if not _KEY_PATTERN.match(key):
        issues.append(ComplianceIssue(
            key=key,
            rule="key_naming",
            severity="warning",
        ))
    return issues


def _check_value_not_empty(key: str, value: str) -> List[ComplianceIssue]:
    issues: List[ComplianceIssue] = []
    if not value.strip():
        issues.append(ComplianceIssue(
            key=key,
            rule="no_empty_values",
            severity="error",
        ))
    return issues


def _check_forbidden_plaintext(key: str, value: str) -> List[ComplianceIssue]:
    issues: List[ComplianceIssue] = []
    upper_key = key.upper()
    for prefix in _FORBIDDEN_PREFIXES:
        if upper_key.startswith(prefix) and len(value) < 16:
            issues.append(ComplianceIssue(
                key=key,
                rule="weak_sensitive_value",
                severity="error",
            ))
            break
    return issues


def run_compliance(vault_path: Path, password: str) -> ComplianceReport:
    """Run all compliance checks against a vault and return a report."""
    vault = load_vault(vault_path, password)
    report = ComplianceReport()
    for key, value in vault.items():
        report.issues.extend(_check_key_naming(key))
        report.issues.extend(_check_value_not_empty(key, value))
        report.issues.extend(_check_forbidden_plaintext(key, value))
    return report
