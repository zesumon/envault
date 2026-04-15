"""Tests for envault.groups module."""

import pytest
from pathlib import Path

from envault.groups import (
    add_key_to_group,
    create_group,
    delete_group,
    find_groups_for_key,
    get_group_keys,
    list_groups,
    remove_key_from_group,
)
from envault.storage import set_secret, get_vault_path


@pytest.fixture
def vault_path(tmp_path):
    return tmp_path / ".envault" / "default" / "vault.enc"


def _add_key(vault_path, key, value="secret", password="pw"):
    set_secret(vault_path, key, value, password)


def test_list_groups_empty_when_no_file(vault_path):
    assert list_groups(vault_path) == []


def test_create_group_adds_to_list(vault_path):
    create_group(vault_path, "backend")
    assert "backend" in list_groups(vault_path)


def test_create_group_invalid_name_raises(vault_path):
    with pytest.raises(ValueError, match="Invalid group name"):
        create_group(vault_path, "my-group")


def test_create_duplicate_group_raises(vault_path):
    create_group(vault_path, "backend")
    with pytest.raises(ValueError, match="already exists"):
        create_group(vault_path, "backend")


def test_delete_group_removes_from_list(vault_path):
    create_group(vault_path, "backend")
    delete_group(vault_path, "backend")
    assert "backend" not in list_groups(vault_path)


def test_delete_missing_group_raises(vault_path):
    with pytest.raises(KeyError):
        delete_group(vault_path, "nonexistent")


def test_add_key_to_group(vault_path):
    _add_key(vault_path, "DB_URL")
    create_group(vault_path, "db")
    add_key_to_group(vault_path, "db", "DB_URL")
    assert "DB_URL" in get_group_keys(vault_path, "db")


def test_add_key_to_group_missing_key_raises(vault_path):
    create_group(vault_path, "db")
    with pytest.raises(KeyError, match="not found in vault"):
        add_key_to_group(vault_path, "db", "MISSING")


def test_add_key_to_missing_group_raises(vault_path):
    _add_key(vault_path, "DB_URL")
    with pytest.raises(KeyError, match="not found"):
        add_key_to_group(vault_path, "nogroup", "DB_URL")


def test_add_key_is_idempotent(vault_path):
    _add_key(vault_path, "DB_URL")
    create_group(vault_path, "db")
    add_key_to_group(vault_path, "db", "DB_URL")
    add_key_to_group(vault_path, "db", "DB_URL")
    assert get_group_keys(vault_path, "db").count("DB_URL") == 1


def test_remove_key_from_group(vault_path):
    _add_key(vault_path, "DB_URL")
    create_group(vault_path, "db")
    add_key_to_group(vault_path, "db", "DB_URL")
    remove_key_from_group(vault_path, "db", "DB_URL")
    assert "DB_URL" not in get_group_keys(vault_path, "db")


def test_remove_missing_key_from_group_raises(vault_path):
    create_group(vault_path, "db")
    with pytest.raises(KeyError):
        remove_key_from_group(vault_path, "db", "MISSING")


def test_find_groups_for_key(vault_path):
    _add_key(vault_path, "API_KEY")
    create_group(vault_path, "frontend")
    create_group(vault_path, "backend")
    add_key_to_group(vault_path, "frontend", "API_KEY")
    add_key_to_group(vault_path, "backend", "API_KEY")
    groups = find_groups_for_key(vault_path, "API_KEY")
    assert groups == ["backend", "frontend"]


def test_get_group_keys_sorted(vault_path):
    for k in ["ZEBRA", "ALPHA", "MANGO"]:
        _add_key(vault_path, k)
    create_group(vault_path, "misc")
    for k in ["ZEBRA", "ALPHA", "MANGO"]:
        add_key_to_group(vault_path, "misc", k)
    assert get_group_keys(vault_path, "misc") == ["ALPHA", "MANGO", "ZEBRA"]
