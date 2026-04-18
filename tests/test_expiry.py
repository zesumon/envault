import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path

from envault.storage import save_vault
from envault.expiry import (
    set_expiry, get_expiry, remove_expiry,
    list_expired, list_expiry, purge_expired,
)

PASSWORD = "testpass"


@pytest.fixture
def vault_path(tmp_path):
    vp = tmp_path / "vault" / "secrets.db"
    vp.parent.mkdir(parents=True)
    save_vault(vp, {"API_KEY": "abc", "TOKEN": "xyz", "OLD": "val"}, PASSWORD)
    return vp


def _future(days=10):
    return datetime.now(timezone.utc) + timedelta(days=days)


def _past(days=1):
    return datetime.now(timezone.utc) - timedelta(days=days)


def test_get_expiry_returns_none_when_not_set(vault_path):
    assert get_expiry(vault_path, "API_KEY") is None


def test_set_and_get_expiry(vault_path):
    dt = _future()
    iso = set_expiry(vault_path, "API_KEY", dt)
    assert get_expiry(vault_path, "API_KEY") == iso
    assert "T" in iso


def test_remove_expiry(vault_path):
    set_expiry(vault_path, "TOKEN", _future())
    assert remove_expiry(vault_path, "TOKEN") is True
    assert get_expiry(vault_path, "TOKEN") is None


def test_remove_expiry_missing_returns_false(vault_path):
    assert remove_expiry(vault_path, "NOPE") is False


def test_list_expired_empty_when_none_set(vault_path):
    assert list_expired(vault_path) == []


def test_list_expired_returns_past_keys(vault_path):
    set_expiry(vault_path, "OLD", _past())
    set_expiry(vault_path, "TOKEN", _future())
    expired = list_expired(vault_path)
    assert "OLD" in expired
    assert "TOKEN" not in expired


def test_list_expiry_returns_all(vault_path):
    set_expiry(vault_path, "API_KEY", _future())
    set_expiry(vault_path, "TOKEN", _past())
    items = list_expiry(vault_path)
    keys = [k for k, _ in items]
    assert "API_KEY" in keys
    assert "TOKEN" in keys


def test_purge_expired_removes_keys(vault_path):
    set_expiry(vault_path, "OLD", _past())
    removed = purge_expired(vault_path, PASSWORD)
    assert "OLD" in removed


def test_purge_expired_keys_gone_from_vault(vault_path):
    from envault.storage import load_vault
    set_expiry(vault_path, "OLD", _past())
    purge_expired(vault_path, PASSWORD)
    vault = load_vault(vault_path, PASSWORD)
    assert "OLD" not in vault


def test_purge_nothing_returns_empty(vault_path):
    assert purge_expired(vault_path, PASSWORD) == []
