"""Tests for envault.rotate."""

from __future__ import annotations

import pytest

from cryptography.fernet import InvalidToken

from envault.storage import set_secret, get_secret, load_vault
from envault.rotate import rotate_password, rotate_dry_run


@pytest.fixture()
def vault_path(tmp_path):
    return str(tmp_path / "vault" / "default.vault")


def _populate(vault_path: str, password: str) -> None:
    set_secret(vault_path, password, "KEY_A", "alpha")
    set_secret(vault_path, password, "KEY_B", "beta")
    set_secret(vault_path, password, "KEY_C", "gamma")


def test_rotate_returns_count(vault_path):
    _populate(vault_path, "old")
    count = rotate_password(vault_path, "old", "new")
    assert count == 3


def test_rotate_secrets_readable_with_new_password(vault_path):
    _populate(vault_path, "old")
    rotate_password(vault_path, "old", "new")

    assert get_secret(vault_path, "new", "KEY_A") == "alpha"
    assert get_secret(vault_path, "new", "KEY_B") == "beta"
    assert get_secret(vault_path, "new", "KEY_C") == "gamma"


def test_rotate_old_password_no_longer_works(vault_path):
    _populate(vault_path, "old")
    rotate_password(vault_path, "old", "new")

    with pytest.raises((InvalidToken, Exception)):
        load_vault(vault_path, "old")


def test_rotate_wrong_old_password_raises(vault_path):
    _populate(vault_path, "correct")
    with pytest.raises((InvalidToken, Exception)):
        rotate_password(vault_path, "wrong", "new")


def test_rotate_empty_vault_returns_zero(vault_path):
    # create an empty vault by saving with no secrets
    from envault.storage import save_vault
    save_vault(vault_path, "old", {})
    count = rotate_password(vault_path, "old", "new")
    assert count == 0


def test_dry_run_returns_keys_without_writing(vault_path):
    _populate(vault_path, "pass")
    keys = rotate_dry_run(vault_path, "pass")
    assert set(keys) == {"KEY_A", "KEY_B", "KEY_C"}
    # original password still works — nothing was written
    assert get_secret(vault_path, "pass", "KEY_A") == "alpha"


def test_dry_run_missing_vault_returns_none(vault_path):
    result = rotate_dry_run(vault_path, "pass")
    assert result is None
