"""Tests for envault.lint."""
from __future__ import annotations

import os
import pytest

from envault.storage import save_vault, set_secret, get_vault_path
from envault.lint import lint_vault, LintIssue


@pytest.fixture()
def vault_path(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    return get_vault_path()


PASSWORD = "testpass"


def _populate(vault_path, pairs: dict):
    for k, v in pairs.items():
        set_secret(vault_path, PASSWORD, k, v)


def test_lint_clean_vault_returns_no_issues(vault_path):
    _populate(vault_path, {"DATABASE_URL": "postgres://localhost/db", "API_KEY": "abc123xyz"})
    result = lint_vault(vault_path, PASSWORD)
    assert result.issues == []
    assert result.ok is True


def test_lint_detects_empty_value(vault_path):
    _populate(vault_path, {"EMPTY_KEY": ""})
    result = lint_vault(vault_path, PASSWORD)
    errors = [i for i in result.issues if i.severity == "error" and i.key == "EMPTY_KEY"]
    assert len(errors) == 1
    assert result.ok is False


def test_lint_detects_weak_value(vault_path):
    _populate(vault_path, {"DB_PASSWORD": "changeme"})
    result = lint_vault(vault_path, PASSWORD)
    warnings = [i for i in result.warnings if i.key == "DB_PASSWORD"]
    assert len(warnings) == 1


def test_lint_detects_bad_key_naming(vault_path):
    _populate(vault_path, {"badKeyName": "somevalue"})
    result = lint_vault(vault_path, PASSWORD)
    warnings = [i for i in result.warnings if i.key == "badKeyName"]
    assert len(warnings) == 1
    assert "UPPER_SNAKE_CASE" in warnings[0].message


def test_lint_multiple_issues(vault_path):
    _populate(vault_path, {
        "good_key": "",          # bad name + empty value
        "STRONG_KEY": "realvalue",
        "WEAK": "password",
    })
    result = lint_vault(vault_path, PASSWORD)
    keys_with_issues = {i.key for i in result.issues}
    assert "good_key" in keys_with_issues
    assert "WEAK" in keys_with_issues
    assert "STRONG_KEY" not in keys_with_issues


def test_lint_ok_property_false_on_errors(vault_path):
    _populate(vault_path, {"MISSING_VALUE": ""})
    result = lint_vault(vault_path, PASSWORD)
    assert result.ok is False


def test_lint_ok_property_true_with_only_warnings(vault_path):
    _populate(vault_path, {"lower_case": "strongvalue123"})
    result = lint_vault(vault_path, PASSWORD)
    assert result.warnings
    assert result.ok is True
