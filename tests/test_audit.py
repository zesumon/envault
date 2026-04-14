"""Tests for envault.audit module."""

import pytest
from pathlib import Path

from envault.audit import log_event, read_events, clear_audit_log, get_audit_path


@pytest.fixture
def audit_dir(tmp_path):
    return tmp_path / "vault"


def test_read_events_returns_empty_when_no_log(audit_dir):
    events = read_events(vault_dir=audit_dir)
    assert events == []


def test_log_event_creates_file(audit_dir):
    log_event("set", "MY_KEY", vault_dir=audit_dir)
    assert get_audit_path(audit_dir).exists()


def test_log_event_records_action_and_key(audit_dir):
    log_event("set", "DB_URL", vault_dir=audit_dir)
    events = read_events(vault_dir=audit_dir)
    assert len(events) == 1
    assert events[0]["action"] == "set"
    assert events[0]["key"] == "DB_URL"


def test_log_event_has_timestamp(audit_dir):
    log_event("get", "API_KEY", vault_dir=audit_dir)
    events = read_events(vault_dir=audit_dir)
    assert "timestamp" in events[0]
    assert events[0]["timestamp"].endswith("+00:00")


def test_multiple_events_appended(audit_dir):
    log_event("set", "FOO", vault_dir=audit_dir)
    log_event("get", "FOO", vault_dir=audit_dir)
    log_event("delete", "FOO", vault_dir=audit_dir)
    events = read_events(vault_dir=audit_dir)
    assert len(events) == 3
    actions = [e["action"] for e in events]
    assert actions == ["set", "get", "delete"]


def test_clear_audit_log_removes_file(audit_dir):
    log_event("set", "X", vault_dir=audit_dir)
    clear_audit_log(vault_dir=audit_dir)
    assert not get_audit_path(audit_dir).exists()


def test_clear_audit_log_noop_when_missing(audit_dir):
    # Should not raise even if file doesn't exist
    clear_audit_log(vault_dir=audit_dir)


def test_read_events_after_clear_is_empty(audit_dir):
    log_event("set", "Z", vault_dir=audit_dir)
    clear_audit_log(vault_dir=audit_dir)
    assert read_events(vault_dir=audit_dir) == []
