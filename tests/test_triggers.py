"""Tests for envault.triggers."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.triggers import (
    add_trigger,
    clear_triggers,
    get_triggers,
    list_triggers,
    remove_trigger,
)


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "vault.enc"


def test_get_triggers_empty_when_no_file(vault_path):
    result = get_triggers(vault_path, "MY_KEY")
    assert result == {}


def test_list_triggers_empty_when_no_file(vault_path):
    assert list_triggers(vault_path) == {}


def test_add_trigger_and_retrieve(vault_path):
    add_trigger(vault_path, "API_KEY", "on_set", "echo set")
    result = get_triggers(vault_path, "API_KEY")
    assert "on_set" in result
    assert "echo set" in result["on_set"]


def test_add_multiple_triggers_same_key_event(vault_path):
    add_trigger(vault_path, "DB_URL", "on_set", "echo a")
    add_trigger(vault_path, "DB_URL", "on_set", "echo b")
    result = get_triggers(vault_path, "DB_URL")
    assert result["on_set"] == ["echo a", "echo b"]


def test_add_duplicate_trigger_is_idempotent(vault_path):
    add_trigger(vault_path, "TOKEN", "on_delete", "notify.sh")
    add_trigger(vault_path, "TOKEN", "on_delete", "notify.sh")
    result = get_triggers(vault_path, "TOKEN")
    assert result["on_delete"].count("notify.sh") == 1


def test_add_trigger_invalid_event_raises(vault_path):
    with pytest.raises(ValueError, match="Invalid event"):
        add_trigger(vault_path, "KEY", "on_magic", "cmd")


def test_remove_trigger_returns_true(vault_path):
    add_trigger(vault_path, "KEY", "on_get", "log.sh")
    assert remove_trigger(vault_path, "KEY", "on_get", "log.sh") is True


def test_remove_trigger_cleans_up_empty_structures(vault_path):
    add_trigger(vault_path, "KEY", "on_get", "log.sh")
    remove_trigger(vault_path, "KEY", "on_get", "log.sh")
    assert list_triggers(vault_path) == {}


def test_remove_missing_trigger_returns_false(vault_path):
    assert remove_trigger(vault_path, "GHOST", "on_set", "cmd") is False


def test_get_triggers_filtered_by_event(vault_path):
    add_trigger(vault_path, "X", "on_set", "a")
    add_trigger(vault_path, "X", "on_delete", "b")
    result = get_triggers(vault_path, "X", event="on_set")
    assert "on_set" in result
    assert "on_delete" not in result


def test_clear_triggers_removes_all_for_key(vault_path):
    add_trigger(vault_path, "K", "on_set", "cmd1")
    add_trigger(vault_path, "K", "on_expire", "cmd2")
    clear_triggers(vault_path, "K")
    assert get_triggers(vault_path, "K") == {}


def test_clear_triggers_leaves_other_keys(vault_path):
    add_trigger(vault_path, "A", "on_set", "cmd")
    add_trigger(vault_path, "B", "on_set", "cmd")
    clear_triggers(vault_path, "A")
    remaining = list_triggers(vault_path)
    assert "A" not in remaining
    assert "B" in remaining
