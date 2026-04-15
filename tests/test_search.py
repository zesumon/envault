"""Tests for envault.search module."""

import pytest

from envault.search import search_keys, search_values, list_keys
from envault.storage import save_vault, get_vault_path
from envault.crypto import encrypt


PASSWORD = "hunter2"


@pytest.fixture()
def vault_path(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    path = get_vault_path("default")
    return path


def _make_vault(vault_path, entries: dict[str, str]):
    data = {key: encrypt(value, PASSWORD) for key, value in entries.items()}
    save_vault(vault_path, data)


def test_list_keys_empty(vault_path):
    result = list_keys(PASSWORD, vault_path=str(vault_path))
    assert result == []


def test_list_keys_returns_sorted(vault_path):
    _make_vault(vault_path, {"ZEBRA": "z", "ALPHA": "a", "MIDDLE": "m"})
    result = list_keys(PASSWORD, vault_path=str(vault_path))
    assert result == ["ALPHA", "MIDDLE", "ZEBRA"]


def test_search_keys_exact(vault_path):
    _make_vault(vault_path, {"DB_HOST": "localhost", "DB_PORT": "5432", "API_KEY": "secret"})
    result = search_keys(PASSWORD, "DB_HOST", vault_path=str(vault_path))
    assert result == ["DB_HOST"]


def test_search_keys_wildcard(vault_path):
    _make_vault(vault_path, {"DB_HOST": "localhost", "DB_PORT": "5432", "API_KEY": "secret"})
    result = search_keys(PASSWORD, "DB_*", vault_path=str(vault_path))
    assert result == ["DB_HOST", "DB_PORT"]


def test_search_keys_case_insensitive(vault_path):
    _make_vault(vault_path, {"DB_HOST": "localhost", "API_KEY": "secret"})
    result = search_keys(PASSWORD, "db_*", vault_path=str(vault_path))
    assert result == ["DB_HOST"]


def test_search_keys_no_match(vault_path):
    _make_vault(vault_path, {"DB_HOST": "localhost"})
    result = search_keys(PASSWORD, "REDIS_*", vault_path=str(vault_path))
    assert result == []


def test_search_values_finds_substring(vault_path):
    _make_vault(vault_path, {"DB_HOST": "localhost", "REDIS_HOST": "redis.local", "API_KEY": "abc123"})
    result = search_values(PASSWORD, "local", vault_path=str(vault_path))
    keys = [k for k, _ in result]
    assert "DB_HOST" in keys
    assert "REDIS_HOST" in keys
    assert "API_KEY" not in keys


def test_search_values_case_insensitive(vault_path):
    _make_vault(vault_path, {"SECRET": "MySecretValue"})
    result = search_values(PASSWORD, "mysecret", vault_path=str(vault_path))
    assert len(result) == 1
    assert result[0][0] == "SECRET"


def test_search_values_returns_sorted(vault_path):
    _make_vault(vault_path, {"ZEBRA_URL": "http://example.com", "ALPHA_URL": "http://example.com"})
    result = search_values(PASSWORD, "example", vault_path=str(vault_path))
    assert [k for k, _ in result] == ["ALPHA_URL", "ZEBRA_URL"]


def test_search_values_no_match(vault_path):
    _make_vault(vault_path, {"KEY": "value"})
    result = search_values(PASSWORD, "nope", vault_path=str(vault_path))
    assert result == []
