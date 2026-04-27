"""Tests for envault.compliance."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.storage import save_vault
from envault.compliance import run_compliance, ComplianceReport


@pytest.fixture()
def vault_path(tmp_path) -> Path:
    return tmp_path / "vault" / "default.vault"


def _make_vault(vault_path: Path, secrets: dict, password: str = "pw"):
    vault_path.parent.mkdir(parents=True, exist_ok=True)
    save_vault(vault_path, secrets, password)


def test_compliance_passes_clean_vault(vault_path):
    _make_vault(vault_path, {"DATABASE_URL": "postgres://localhost/db"})
    report = run_compliance(vault_path, "pw")
    assert report.passed
    assert report.issues == []


def test_compliance_detects_empty_value(vault_path):
    _make_vault(vault_path, {"API_KEY": ""})
    report = run_compliance(vault_path, "pw")
    assert not report.passed
    errors = [i.rule for i in report.errors]
    assert "no_empty_values" in errors


def test_compliance_warns_on_bad_key_naming(vault_path):
    _make_vault(vault_path, {"myLowercaseKey": "value123"})
    report = run_compliance(vault_path, "pw")
    warnings = [i.rule for i in report.warnings]
    assert "key_naming" in warnings


def test_compliance_errors_on_weak_sensitive_value(vault_path):
    _make_vault(vault_path, {"PASSWORD_MAIN": "short"})
    report = run_compliance(vault_path, "pw")
    assert not report.passed
    rules = [i.rule for i in report.errors]
    assert "weak_sensitive_value" in rules


def test_compliance_strong_sensitive_value_passes(vault_path):
    _make_vault(vault_path, {"TOKEN_SECRET": "a" * 32})
    report = run_compliance(vault_path, "pw")
    sensitive_errors = [i for i in report.errors if i.rule == "weak_sensitive_value"]
    assert sensitive_errors == []


def test_compliance_multiple_issues(vault_path):
    _make_vault(vault_path, {
        "bad-key": "",
        "GOOD_KEY": "valid_value",
        "TOKEN_X": "weak",
    })
    report = run_compliance(vault_path, "pw")
    rules = [i.rule for i in report.issues]
    assert "no_empty_values" in rules
    assert "key_naming" in rules
    assert "weak_sensitive_value" in rules


def test_compliance_report_passed_property_true_when_no_errors(vault_path):
    _make_vault(vault_path, {"lowercasekey": "some_value"})
    report = run_compliance(vault_path, "pw")
    # only a warning, no errors → passed should be True
    assert report.passed
    assert len(report.warnings) >= 1
