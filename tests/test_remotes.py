"""Unit tests for envault.remotes."""

import pytest
from pathlib import Path

from envault.remotes import (
    list_remotes,
    add_remote,
    update_remote,
    remove_remote,
    get_remote,
)


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


def test_list_remotes_empty_when_no_file(vault_dir):
    assert list_remotes(vault_dir) == []


def test_add_and_list_remote(vault_dir):
    add_remote(vault_dir, "origin", "https://example.com/vault")
    remotes = list_remotes(vault_dir)
    assert len(remotes) == 1
    assert remotes[0]["name"] == "origin"
    assert remotes[0]["url"] == "https://example.com/vault"


def test_list_remotes_sorted_by_name(vault_dir):
    add_remote(vault_dir, "zebra", "https://z.example.com")
    add_remote(vault_dir, "alpha", "https://a.example.com")
    names = [r["name"] for r in list_remotes(vault_dir)]
    assert names == ["alpha", "zebra"]


def test_add_duplicate_remote_raises(vault_dir):
    add_remote(vault_dir, "origin", "https://example.com")
    with pytest.raises(KeyError, match="already exists"):
        add_remote(vault_dir, "origin", "https://other.com")


def test_add_invalid_name_raises(vault_dir):
    with pytest.raises(ValueError, match="Invalid remote name"):
        add_remote(vault_dir, "bad name!", "https://example.com")


def test_add_empty_url_raises(vault_dir):
    with pytest.raises(ValueError, match="must not be empty"):
        add_remote(vault_dir, "origin", "   ")


def test_get_remote_returns_url(vault_dir):
    add_remote(vault_dir, "origin", "https://example.com")
    assert get_remote(vault_dir, "origin") == "https://example.com"


def test_get_remote_missing_returns_none(vault_dir):
    assert get_remote(vault_dir, "nope") is None


def test_update_remote_changes_url(vault_dir):
    add_remote(vault_dir, "origin", "https://old.example.com")
    update_remote(vault_dir, "origin", "https://new.example.com")
    assert get_remote(vault_dir, "origin") == "https://new.example.com"


def test_update_missing_remote_raises(vault_dir):
    with pytest.raises(KeyError, match="not found"):
        update_remote(vault_dir, "ghost", "https://example.com")


def test_remove_remote(vault_dir):
    add_remote(vault_dir, "origin", "https://example.com")
    remove_remote(vault_dir, "origin")
    assert list_remotes(vault_dir) == []


def test_remove_missing_remote_raises(vault_dir):
    with pytest.raises(KeyError, match="not found"):
        remove_remote(vault_dir, "ghost")
