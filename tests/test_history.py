"""Tests for envault.history."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.history import (
    all_keys_with_history,
    clear_key_history,
    get_key_history,
    record_change,
    _get_history_path,
)


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / ".envault" / "vault.enc"


def test_get_key_history_empty_when_no_file(vault_path: Path) -> None:
    assert get_key_history(vault_path, "FOO") == []


def test_record_change_creates_history_file(vault_path: Path) -> None:
    record_change(vault_path, "API_KEY", "set", "abc***")
    assert _get_history_path(vault_path).exists()


def test_record_change_stores_action_and_preview(vault_path: Path) -> None:
    record_change(vault_path, "DB_URL", "set", "pos***")
    records = get_key_history(vault_path, "DB_URL")
    assert len(records) == 1
    assert records[0]["action"] == "set"
    assert records[0]["preview"] == "pos***"


def test_record_delete_has_no_preview(vault_path: Path) -> None:
    record_change(vault_path, "OLD_KEY", "delete")
    records = get_key_history(vault_path, "OLD_KEY")
    assert records[0]["action"] == "delete"
    assert "preview" not in records[0]


def test_multiple_records_accumulate(vault_path: Path) -> None:
    for i in range(3):
        record_change(vault_path, "TOKEN", "set", f"val{i}***")
    assert len(get_key_history(vault_path, "TOKEN")) == 3


def test_records_have_timestamp(vault_path: Path) -> None:
    record_change(vault_path, "KEY", "set", "x***")
    rec = get_key_history(vault_path, "KEY")[0]
    assert "timestamp" in rec
    assert "T" in rec["timestamp"]  # ISO format


def test_all_keys_with_history_sorted(vault_path: Path) -> None:
    record_change(vault_path, "ZEBRA", "set", "z***")
    record_change(vault_path, "ALPHA", "set", "a***")
    keys = all_keys_with_history(vault_path)
    assert keys == ["ALPHA", "ZEBRA"]


def test_clear_key_history_returns_count(vault_path: Path) -> None:
    record_change(vault_path, "FOO", "set", "f***")
    record_change(vault_path, "FOO", "set", "g***")
    count = clear_key_history(vault_path, "FOO")
    assert count == 2


def test_clear_key_history_removes_entries(vault_path: Path) -> None:
    record_change(vault_path, "BAR", "set", "b***")
    clear_key_history(vault_path, "BAR")
    assert get_key_history(vault_path, "BAR") == []


def test_clear_missing_key_returns_zero(vault_path: Path) -> None:
    assert clear_key_history(vault_path, "NOPE") == 0


def test_history_file_is_valid_json(vault_path: Path) -> None:
    record_change(vault_path, "X", "set", "x***")
    raw = _get_history_path(vault_path).read_text(encoding="utf-8")
    data = json.loads(raw)
    assert isinstance(data, dict)
