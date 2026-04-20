"""Tests for envault.storage module."""

import pytest
from pathlib import Path

from envault.storage import (
    load_vault,
    save_vault,
    set_secret,
    get_secret,
    delete_secret,
    list_keys,
    get_vault_path,
)

PASSWORD = "hunter2"


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "test_vault.enc"


def test_load_vault_returns_empty_when_missing(vault_path):
    result = load_vault(PASSWORD, vault_path)
    assert result == {}


def test_save_and_load_roundtrip(vault_path):
    data = {"DB_HOST": "localhost", "API_KEY": "abc123"}
    save_vault(data, PASSWORD, vault_path)
    loaded = load_vault(PASSWORD, vault_path)
    assert loaded == data


def test_set_and_get_secret(vault_path):
    set_secret("MY_KEY", "my_value", PASSWORD, vault_path)
    value = get_secret("MY_KEY", PASSWORD, vault_path)
    assert value == "my_value"


def test_get_secret_missing_returns_none(vault_path):
    assert get_secret("NONEXISTENT", PASSWORD, vault_path) is None


def test_set_secret_overwrites_existing(vault_path):
    set_secret("KEY", "old", PASSWORD, vault_path)
    set_secret("KEY", "new", PASSWORD, vault_path)
    assert get_secret("KEY", PASSWORD, vault_path) == "new"


def test_delete_secret_removes_key(vault_path):
    set_secret("TO_DELETE", "bye", PASSWORD, vault_path)
    removed = delete_secret("TO_DELETE", PASSWORD, vault_path)
    assert removed is True
    assert get_secret("TO_DELETE", PASSWORD, vault_path) is None


def test_delete_secret_returns_false_when_missing(vault_path):
    assert delete_secret("GHOST", PASSWORD, vault_path) is False


def test_list_keys_sorted(vault_path):
    set_secret("ZEBRA", "1", PASSWORD, vault_path)
    set_secret("ALPHA", "2", PASSWORD, vault_path)
    set_secret("MIDDLE", "3", PASSWORD, vault_path)
    assert list_keys(PASSWORD, vault_path) == ["ALPHA", "MIDDLE", "ZEBRA"]


def test_list_keys_empty_vault(vault_path):
    """list_keys on a fresh vault should return an empty list, not error out."""
    assert list_keys(PASSWORD, vault_path) == []


def test_wrong_password_raises_on_load(vault_path):
    save_vault({"K": "V"}, PASSWORD, vault_path)
    with pytest.raises(Exception):
        load_vault("wrongpassword", vault_path)


def test_get_vault_path_default():
    path = get_vault_path()
    assert path.name == "vault.enc"
    assert ".envault" in str(path)
