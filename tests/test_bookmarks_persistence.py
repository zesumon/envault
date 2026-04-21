"""Persistence tests for envault.bookmarks."""

import json
import pytest
from pathlib import Path

from envault.bookmarks import add_bookmark, remove_bookmark, list_bookmarks, _get_bookmarks_path


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


@pytest.fixture
def vault_path(vault_dir):
    return vault_dir / "vault.enc"


def test_bookmarks_file_is_valid_json(vault_path):
    add_bookmark(vault_path, "key1", "API_TOKEN")
    p = _get_bookmarks_path(vault_path)
    data = json.loads(p.read_text())
    assert "key1" in data
    assert data["key1"]["key"] == "API_TOKEN"


def test_multiple_bookmarks_persist(vault_path):
    add_bookmark(vault_path, "a", "KEY_A")
    add_bookmark(vault_path, "b", "KEY_B")
    add_bookmark(vault_path, "c", "KEY_C")
    entries = list_bookmarks(vault_path)
    assert len(entries) == 3
    keys = {e["name"] for e in entries}
    assert keys == {"a", "b", "c"}


def test_remove_leaves_others_intact(vault_path):
    add_bookmark(vault_path, "x", "X_KEY")
    add_bookmark(vault_path, "y", "Y_KEY")
    remove_bookmark(vault_path, "x")
    entries = list_bookmarks(vault_path)
    assert len(entries) == 1
    assert entries[0]["name"] == "y"


def test_note_persists_across_reload(vault_path):
    add_bookmark(vault_path, "noted", "NOTED_KEY", note="remember this")
    # Simulate reload by calling list_bookmarks fresh
    entries = list_bookmarks(vault_path)
    assert entries[0]["note"] == "remember this"


def test_overwrite_updates_in_file(vault_path):
    add_bookmark(vault_path, "dup", "OLD_KEY")
    add_bookmark(vault_path, "dup", "NEW_KEY")
    p = _get_bookmarks_path(vault_path)
    data = json.loads(p.read_text())
    assert data["dup"]["key"] == "NEW_KEY"
    assert list(data.keys()).count("dup") == 1
