"""Tests for envault.watchers."""
import json
import pytest
from pathlib import Path

from envault.watchers import (
    add_watcher,
    clear_watchers,
    get_watchers,
    list_all_watchers,
    remove_watcher,
    _get_watchers_path,
)


@pytest.fixture()
def vault_path(tmp_path):
    vp = tmp_path / "vault" / "default.vault"
    vp.parent.mkdir(parents=True)
    # Write a minimal vault JSON so key-existence checks pass
    vp.write_text(json.dumps({"API_KEY": "enc", "DB_PASS": "enc"}))
    return vp


def test_get_watchers_empty_when_no_file(vault_path):
    assert get_watchers(vault_path, "API_KEY") == []


def test_add_watcher_and_retrieve(vault_path):
    add_watcher(vault_path, "API_KEY", "alice")
    assert "alice" in get_watchers(vault_path, "API_KEY")


def test_add_duplicate_watcher_is_idempotent(vault_path):
    add_watcher(vault_path, "API_KEY", "alice")
    add_watcher(vault_path, "API_KEY", "alice")
    assert get_watchers(vault_path, "API_KEY").count("alice") == 1


def test_add_watcher_missing_key_raises(vault_path):
    with pytest.raises(KeyError):
        add_watcher(vault_path, "MISSING_KEY", "alice")


def test_add_multiple_watchers(vault_path):
    add_watcher(vault_path, "API_KEY", "alice")
    add_watcher(vault_path, "API_KEY", "bob")
    watchers = get_watchers(vault_path, "API_KEY")
    assert "alice" in watchers
    assert "bob" in watchers


def test_watchers_are_sorted(vault_path):
    add_watcher(vault_path, "API_KEY", "zara")
    add_watcher(vault_path, "API_KEY", "alice")
    watchers = get_watchers(vault_path, "API_KEY")
    assert watchers == sorted(watchers)


def test_remove_watcher_returns_true(vault_path):
    add_watcher(vault_path, "API_KEY", "alice")
    assert remove_watcher(vault_path, "API_KEY", "alice") is True


def test_remove_watcher_absent_returns_false(vault_path):
    assert remove_watcher(vault_path, "API_KEY", "ghost") is False


def test_remove_watcher_cleans_up_empty_key(vault_path):
    add_watcher(vault_path, "API_KEY", "alice")
    remove_watcher(vault_path, "API_KEY", "alice")
    all_w = list_all_watchers(vault_path)
    assert "API_KEY" not in all_w


def test_list_all_watchers(vault_path):
    add_watcher(vault_path, "API_KEY", "alice")
    add_watcher(vault_path, "DB_PASS", "bob")
    all_w = list_all_watchers(vault_path)
    assert set(all_w.keys()) == {"API_KEY", "DB_PASS"}


def test_clear_watchers_returns_count(vault_path):
    add_watcher(vault_path, "API_KEY", "alice")
    add_watcher(vault_path, "API_KEY", "bob")
    count = clear_watchers(vault_path, "API_KEY")
    assert count == 2
    assert get_watchers(vault_path, "API_KEY") == []


def test_watchers_file_is_valid_json(vault_path):
    add_watcher(vault_path, "API_KEY", "alice")
    p = _get_watchers_path(vault_path)
    data = json.loads(p.read_text())
    assert isinstance(data, dict)
