"""Tests for envault.bookmarks."""

import pytest
from pathlib import Path

from envault.bookmarks import (
    add_bookmark,
    remove_bookmark,
    get_bookmark,
    list_bookmarks,
    resolve_bookmark,
)


@pytest.fixture
def vault_path(tmp_path):
    return tmp_path / "vault.enc"


def test_list_bookmarks_empty_when_no_file(vault_path):
    assert list_bookmarks(vault_path) == []


def test_add_bookmark_and_retrieve(vault_path):
    add_bookmark(vault_path, "mydb", "DATABASE_URL", note="prod db")
    entry = get_bookmark(vault_path, "mydb")
    assert entry["key"] == "DATABASE_URL"
    assert entry["note"] == "prod db"


def test_get_bookmark_missing_returns_none(vault_path):
    assert get_bookmark(vault_path, "nonexistent") is None


def test_add_bookmark_invalid_name_raises(vault_path):
    with pytest.raises(ValueError):
        add_bookmark(vault_path, "bad name!", "SOME_KEY")


def test_add_duplicate_bookmark_overwrites(vault_path):
    add_bookmark(vault_path, "api", "API_KEY")
    add_bookmark(vault_path, "api", "NEW_API_KEY", note="updated")
    entry = get_bookmark(vault_path, "api")
    assert entry["key"] == "NEW_API_KEY"
    assert entry["note"] == "updated"


def test_remove_bookmark(vault_path):
    add_bookmark(vault_path, "tok", "TOKEN")
    remove_bookmark(vault_path, "tok")
    assert get_bookmark(vault_path, "tok") is None


def test_remove_missing_bookmark_raises(vault_path):
    with pytest.raises(KeyError):
        remove_bookmark(vault_path, "ghost")


def test_list_bookmarks_sorted(vault_path):
    add_bookmark(vault_path, "zebra", "Z_KEY")
    add_bookmark(vault_path, "alpha", "A_KEY")
    add_bookmark(vault_path, "mango", "M_KEY")
    names = [e["name"] for e in list_bookmarks(vault_path)]
    assert names == ["alpha", "mango", "zebra"]


def test_resolve_bookmark_returns_key(vault_path):
    add_bookmark(vault_path, "secret", "SECRET_TOKEN")
    assert resolve_bookmark(vault_path, "secret") == "SECRET_TOKEN"


def test_resolve_missing_bookmark_returns_none(vault_path):
    assert resolve_bookmark(vault_path, "missing") is None


def test_list_bookmarks_includes_note(vault_path):
    add_bookmark(vault_path, "noted", "NOTED_KEY", note="important")
    entries = list_bookmarks(vault_path)
    assert entries[0]["note"] == "important"
