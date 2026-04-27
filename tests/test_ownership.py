"""Tests for envault.ownership module."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.ownership import (
    get_owner,
    list_all_ownership,
    list_owned_keys,
    remove_owner,
    set_owner,
)


@pytest.fixture
def vault_path(tmp_path):
    return tmp_path / "vault.enc"


def test_get_owner_returns_none_when_no_file(vault_path):
    assert get_owner(vault_path, "API_KEY") is None


def test_set_and_get_owner(vault_path):
    set_owner(vault_path, "API_KEY", "alice")
    assert get_owner(vault_path, "API_KEY") == "alice"


def test_set_owner_overwrites_existing(vault_path):
    set_owner(vault_path, "API_KEY", "alice")
    set_owner(vault_path, "API_KEY", "bob")
    assert get_owner(vault_path, "API_KEY") == "bob"


def test_set_owner_strips_whitespace(vault_path):
    set_owner(vault_path, "DB_PASS", "  carol  ")
    assert get_owner(vault_path, "DB_PASS") == "carol"


def test_set_owner_empty_string_raises(vault_path):
    with pytest.raises(ValueError):
        set_owner(vault_path, "API_KEY", "")


def test_set_owner_whitespace_only_raises(vault_path):
    with pytest.raises(ValueError):
        set_owner(vault_path, "API_KEY", "   ")


def test_remove_owner_returns_true_when_removed(vault_path):
    set_owner(vault_path, "API_KEY", "alice")
    result = remove_owner(vault_path, "API_KEY")
    assert result is True
    assert get_owner(vault_path, "API_KEY") is None


def test_remove_owner_returns_false_when_not_found(vault_path):
    result = remove_owner(vault_path, "MISSING_KEY")
    assert result is False


def test_list_owned_keys_returns_sorted(vault_path):
    set_owner(vault_path, "Z_KEY", "alice")
    set_owner(vault_path, "A_KEY", "alice")
    set_owner(vault_path, "M_KEY", "bob")
    owned = list_owned_keys(vault_path, "alice")
    assert owned == ["A_KEY", "Z_KEY"]


def test_list_owned_keys_empty_when_no_match(vault_path):
    set_owner(vault_path, "API_KEY", "alice")
    assert list_owned_keys(vault_path, "nobody") == []


def test_list_all_ownership_returns_full_mapping(vault_path):
    set_owner(vault_path, "API_KEY", "alice")
    set_owner(vault_path, "DB_PASS", "bob")
    data = list_all_ownership(vault_path)
    assert data == {"API_KEY": "alice", "DB_PASS": "bob"}


def test_list_all_ownership_empty_when_no_file(vault_path):
    assert list_all_ownership(vault_path) == {}


def test_ownership_file_is_created(vault_path):
    set_owner(vault_path, "KEY", "alice")
    ownership_file = vault_path.parent / "ownership.json"
    assert ownership_file.exists()
