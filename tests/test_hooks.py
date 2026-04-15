"""Tests for envault.hooks module."""

import json
import pytest
from pathlib import Path

from envault.hooks import (
    add_hook, remove_hook, get_hooks, list_hooks, fire_hooks, _VALID_EVENTS
)


@pytest.fixture
def vault_path(tmp_path):
    return tmp_path / "vault.enc"


def test_get_hooks_empty_when_no_file(vault_path):
    assert get_hooks(vault_path, "post-set") == []


def test_list_hooks_empty_when_no_file(vault_path):
    assert list_hooks(vault_path) == {}


def test_add_hook_and_retrieve(vault_path):
    add_hook(vault_path, "post-set", "echo hello")
    assert "echo hello" in get_hooks(vault_path, "post-set")


def test_add_multiple_hooks_same_event(vault_path):
    add_hook(vault_path, "post-set", "echo one")
    add_hook(vault_path, "post-set", "echo two")
    hooks = get_hooks(vault_path, "post-set")
    assert hooks == ["echo one", "echo two"]


def test_add_duplicate_hook_raises(vault_path):
    add_hook(vault_path, "pre-set", "make lint")
    with pytest.raises(ValueError, match="already registered"):
        add_hook(vault_path, "pre-set", "make lint")


def test_add_invalid_event_raises(vault_path):
    with pytest.raises(ValueError, match="Unknown event"):
        add_hook(vault_path, "on-magic", "echo nope")


def test_remove_hook(vault_path):
    add_hook(vault_path, "pre-delete", "echo bye")
    remove_hook(vault_path, "pre-delete", "echo bye")
    assert get_hooks(vault_path, "pre-delete") == []


def test_remove_missing_hook_raises(vault_path):
    with pytest.raises(KeyError):
        remove_hook(vault_path, "post-set", "nonexistent")


def test_remove_last_hook_cleans_up_event(vault_path):
    add_hook(vault_path, "post-export", "echo done")
    remove_hook(vault_path, "post-export", "echo done")
    hooks = list_hooks(vault_path)
    assert "post-export" not in hooks


def test_hooks_persisted_as_json(vault_path):
    add_hook(vault_path, "post-import", "notify-send imported")
    hooks_file = vault_path.parent / "hooks.json"
    assert hooks_file.exists()
    data = json.loads(hooks_file.read_text())
    assert "post-import" in data


def test_fire_hooks_returns_executed_commands(vault_path):
    add_hook(vault_path, "post-set", "true")
    executed = fire_hooks(vault_path, "post-set")
    assert executed == ["true"]


def test_fire_hooks_no_hooks_returns_empty(vault_path):
    executed = fire_hooks(vault_path, "post-set")
    assert executed == []


def test_valid_events_set_is_complete():
    assert "pre-set" in _VALID_EVENTS
    assert "post-delete" in _VALID_EVENTS
    assert len(_VALID_EVENTS) == 8
