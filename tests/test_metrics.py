"""Tests for envault.metrics."""

from __future__ import annotations

import os
import pytest

from envault.storage import get_vault_path, save_vault
from envault.audit import log_event
from envault.tags import add_tag
from envault.metrics import compute_metrics, format_metrics, VaultMetrics


@pytest.fixture()
def vault_path(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    return get_vault_path("default")


PASSWORD = "testpass"


def _populate(vault_path: str, data: dict) -> None:
    save_vault(vault_path, PASSWORD, data)


def test_compute_metrics_empty_vault(vault_path):
    _populate(vault_path, {})
    m = compute_metrics(vault_path, PASSWORD)
    assert isinstance(m, VaultMetrics)
    assert m.total_keys == 0
    assert m.total_size_bytes == 0
    assert m.avg_value_length == 0.0


def test_compute_metrics_counts_keys(vault_path):
    _populate(vault_path, {"A": "hello", "B": "world", "C": "!"})
    m = compute_metrics(vault_path, PASSWORD)
    assert m.total_keys == 3


def test_compute_metrics_size(vault_path):
    _populate(vault_path, {"K": "abcde"})
    m = compute_metrics(vault_path, PASSWORD)
    assert m.total_size_bytes == 5
    assert m.avg_value_length == 5.0


def test_compute_metrics_keys_with_tags(vault_path):
    _populate(vault_path, {"A": "val", "B": "val2"})
    add_tag(vault_path, PASSWORD, "A", "important")
    m = compute_metrics(vault_path, PASSWORD)
    assert m.keys_with_tags == 1


def test_compute_metrics_audit_events(vault_path):
    _populate(vault_path, {})
    log_event(vault_path, "set", "FOO")
    log_event(vault_path, "set", "BAR")
    log_event(vault_path, "delete", "FOO")
    m = compute_metrics(vault_path, PASSWORD)
    assert m.total_audit_events == 3
    assert m.action_counts["set"] == 2
    assert m.action_counts["delete"] == 1
    assert m.most_recent_action == "delete"


def test_format_metrics_returns_string(vault_path):
    _populate(vault_path, {"X": "y"})
    m = compute_metrics(vault_path, PASSWORD)
    out = format_metrics(m)
    assert isinstance(out, str)
    assert "Keys" in out
    assert "1" in out


def test_compute_metrics_no_tags_returns_zero(vault_path):
    _populate(vault_path, {"A": "v", "B": "v2"})
    m = compute_metrics(vault_path, PASSWORD)
    assert m.keys_with_tags == 0
