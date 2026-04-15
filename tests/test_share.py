"""Tests for envault/share.py"""

import time
import pytest
from pathlib import Path
from unittest.mock import patch

from envault.storage import set_secret
from envault.share import create_share, open_share, list_shares, delete_share

PASSWORD = "vaultpass"
SHARE_PW = "sharepass"


@pytest.fixture
def vault_path(tmp_path):
    return str(tmp_path / ".envault" / "vault.enc")


def _populate(vault_path):
    set_secret(vault_path, PASSWORD, "API_KEY", "abc123")
    set_secret(vault_path, PASSWORD, "DB_URL", "postgres://localhost/dev")


def test_create_share_returns_filename(vault_path):
    _populate(vault_path)
    slug = create_share(vault_path, PASSWORD, SHARE_PW, ["API_KEY"])
    assert slug.startswith("share_")
    assert slug.endswith(".enc")


def test_create_share_appears_in_list(vault_path):
    _populate(vault_path)
    assert list_shares(vault_path) == []
    slug = create_share(vault_path, PASSWORD, SHARE_PW, ["API_KEY"])
    assert slug in list_shares(vault_path)


def test_open_share_returns_correct_secrets(vault_path):
    _populate(vault_path)
    slug = create_share(vault_path, PASSWORD, SHARE_PW, ["API_KEY", "DB_URL"])
    secrets = open_share(vault_path, slug, SHARE_PW)
    assert secrets["API_KEY"] == "abc123"
    assert secrets["DB_URL"] == "postgres://localhost/dev"


def test_open_share_wrong_password_raises(vault_path):
    _populate(vault_path)
    slug = create_share(vault_path, PASSWORD, SHARE_PW, ["API_KEY"])
    with pytest.raises(Exception):
        open_share(vault_path, slug, "wrongpassword")


def test_open_share_expired_raises(vault_path):
    _populate(vault_path)
    slug = create_share(vault_path, PASSWORD, SHARE_PW, ["API_KEY"], ttl_seconds=1)
    with patch("envault.share.time.time", return_value=time.time() + 9999):
        with pytest.raises(ValueError, match="expired"):
            open_share(vault_path, slug, SHARE_PW)


def test_open_share_missing_raises(vault_path):
    with pytest.raises(FileNotFoundError):
        open_share(vault_path, "nonexistent.enc", SHARE_PW)


def test_create_share_missing_key_raises(vault_path):
    _populate(vault_path)
    with pytest.raises(KeyError, match="MISSING_KEY"):
        create_share(vault_path, PASSWORD, SHARE_PW, ["MISSING_KEY"])


def test_delete_share_removes_file(vault_path):
    _populate(vault_path)
    slug = create_share(vault_path, PASSWORD, SHARE_PW, ["API_KEY"])
    delete_share(vault_path, slug)
    assert slug not in list_shares(vault_path)


def test_delete_share_missing_raises(vault_path):
    with pytest.raises(FileNotFoundError):
        delete_share(vault_path, "ghost.enc")


def test_list_shares_empty_when_no_dir(vault_path):
    assert list_shares(vault_path) == []
