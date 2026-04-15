"""Tests for envault/ttl.py"""

import time
import pytest
from pathlib import Path
from envault.ttl import set_ttl, get_ttl, is_expired, clear_ttl, purge_expired
from envault.storage import save_vault, load_vault

PASSWORD = "test-pass"


@pytest.fixture
def vault_path(tmp_path):
    vp = tmp_path / "vault" / "secrets.enc"
    vp.parent.mkdir(parents=True)
    save_vault(vp, {"API_KEY": "abc123", "DB_PASS": "secret"}, PASSWORD)
    return vp


def test_set_ttl_returns_iso_string(vault_path):
    result = set_ttl(vault_path, "API_KEY", 3600)
    assert "T" in result  # ISO format contains T
    assert "+" in result or "Z" in result or result.endswith("+00:00")


def test_get_ttl_returns_none_when_not_set(vault_path):
    assert get_ttl(vault_path, "API_KEY") is None


def test_get_ttl_returns_value_after_set(vault_path):
    set_ttl(vault_path, "API_KEY", 3600)
    result = get_ttl(vault_path, "API_KEY")
    assert result is not None
    assert "T" in result


def test_is_expired_false_for_future(vault_path):
    set_ttl(vault_path, "API_KEY", 3600)
    assert is_expired(vault_path, "API_KEY") is False


def test_is_expired_true_for_past(vault_path):
    set_ttl(vault_path, "API_KEY", -1)  # already expired
    assert is_expired(vault_path, "API_KEY") is True


def test_is_expired_false_when_no_ttl(vault_path):
    assert is_expired(vault_path, "API_KEY") is False


def test_clear_ttl_removes_entry(vault_path):
    set_ttl(vault_path, "API_KEY", 3600)
    removed = clear_ttl(vault_path, "API_KEY")
    assert removed is True
    assert get_ttl(vault_path, "API_KEY") is None


def test_clear_ttl_returns_false_if_not_set(vault_path):
    assert clear_ttl(vault_path, "NONEXISTENT") is False


def test_purge_expired_removes_keys(vault_path):
    set_ttl(vault_path, "API_KEY", -1)  # expired
    set_ttl(vault_path, "DB_PASS", 3600)  # not expired
    purged = purge_expired(vault_path, PASSWORD)
    assert "API_KEY" in purged
    assert "DB_PASS" not in purged


def test_purge_expired_deletes_from_vault(vault_path):
    set_ttl(vault_path, "API_KEY", -1)
    purge_expired(vault_path, PASSWORD)
    vault = load_vault(vault_path, PASSWORD)
    assert "API_KEY" not in vault
    assert "DB_PASS" in vault


def test_purge_expired_returns_empty_when_nothing_expired(vault_path):
    set_ttl(vault_path, "API_KEY", 3600)
    purged = purge_expired(vault_path, PASSWORD)
    assert purged == []
