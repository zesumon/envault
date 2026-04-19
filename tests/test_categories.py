"""Tests for envault.categories."""
import pytest
from pathlib import Path
from envault.categories import (
    set_category, get_category, remove_category,
    list_by_category, list_all_categories
)
from envault.storage import save_vault


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / ".envault" / "vault.enc"
    p.parent.mkdir(parents=True)
    return p


def _add_key(vault_path, key, value="val", password="pw"):
    from envault.storage import set_secret
    set_secret(vault_path, key, value, password)


def test_get_category_returns_none_when_no_file(vault_path):
    assert get_category(vault_path, "FOO") is None


def test_set_and_get_category(vault_path):
    _add_key(vault_path, "DB_URL")
    set_category(vault_path, "DB_URL", "database")
    assert get_category(vault_path, "DB_URL") == "database"


def test_set_category_invalid_raises(vault_path):
    _add_key(vault_path, "FOO")
    with pytest.raises(ValueError, match="Invalid category"):
        set_category(vault_path, "FOO", "nonsense")


def test_set_category_missing_key_raises(vault_path):
    with pytest.raises(KeyError):
        set_category(vault_path, "MISSING", "api")


def test_set_category_overwrites(vault_path):
    _add_key(vault_path, "API_KEY")
    set_category(vault_path, "API_KEY", "api")
    set_category(vault_path, "API_KEY", "auth")
    assert get_category(vault_path, "API_KEY") == "auth"


def test_remove_category(vault_path):
    _add_key(vault_path, "TOKEN")
    set_category(vault_path, "TOKEN", "auth")
    assert remove_category(vault_path, "TOKEN") is True
    assert get_category(vault_path, "TOKEN") is None


def test_remove_category_not_set_returns_false(vault_path):
    assert remove_category(vault_path, "NOPE") is False


def test_list_by_category(vault_path):
    for k in ["DB_HOST", "DB_PASS", "API_KEY"]:
        _add_key(vault_path, k)
    set_category(vault_path, "DB_HOST", "database")
    set_category(vault_path, "DB_PASS", "database")
    set_category(vault_path, "API_KEY", "api")
    assert list_by_category(vault_path, "database") == ["DB_HOST", "DB_PASS"]
    assert list_by_category(vault_path, "api") == ["API_KEY"]


def test_list_all_categories(vault_path):
    _add_key(vault_path, "X")
    _add_key(vault_path, "Y")
    set_category(vault_path, "X", "misc")
    set_category(vault_path, "Y", "network")
    data = list_all_categories(vault_path)
    assert data["X"] == "misc"
    assert data["Y"] == "network"
