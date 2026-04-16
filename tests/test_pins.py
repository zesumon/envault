"""Tests for envault.pins."""

import pytest
from pathlib import Path
from envault.storage import save_vault
from envault.pins import pin_key, unpin_key, is_pinned, list_pins, assert_not_pinned


@pytest.fixture
def vault_path(tmp_path):
    vp = tmp_path / "vault" / "secrets.db"
    vp.parent.mkdir(parents=True)
    return vp


def _add_key(vault_path, key, value="val"):
    from envault.storage import load_vault
    vault = load_vault(vault_path)
    vault[key] = value
    save_vault(vault_path, vault)


def test_list_pins_empty_when_no_file(vault_path):
    assert list_pins(vault_path) == []


def test_pin_key_and_retrieve(vault_path):
    _add_key(vault_path, "API_KEY")
    pin_key(vault_path, "API_KEY")
    assert is_pinned(vault_path, "API_KEY")


def test_pin_missing_key_raises(vault_path):
    with pytest.raises(KeyError):
        pin_key(vault_path, "GHOST")


def test_unpin_key(vault_path):
    _add_key(vault_path, "DB_PASS")
    pin_key(vault_path, "DB_PASS")
    unpin_key(vault_path, "DB_PASS")
    assert not is_pinned(vault_path, "DB_PASS")


def test_unpin_not_pinned_raises(vault_path):
    _add_key(vault_path, "X")
    with pytest.raises(KeyError):
        unpin_key(vault_path, "X")


def test_list_pins_returns_sorted(vault_path):
    for k in ["Z_KEY", "A_KEY", "M_KEY"]:
        _add_key(vault_path, k)
        pin_key(vault_path, k)
    assert list_pins(vault_path) == ["A_KEY", "M_KEY", "Z_KEY"]


def test_pin_is_idempotent(vault_path):
    _add_key(vault_path, "TOKEN")
    pin_key(vault_path, "TOKEN")
    pin_key(vault_path, "TOKEN")
    assert list_pins(vault_path).count("TOKEN") == 1


def test_assert_not_pinned_raises_for_pinned(vault_path):
    _add_key(vault_path, "SECRET")
    pin_key(vault_path, "SECRET")
    with pytest.raises(PermissionError):
        assert_not_pinned(vault_path, "SECRET")


def test_assert_not_pinned_passes_for_unpinned(vault_path):
    _add_key(vault_path, "FREE")
    assert_not_pinned(vault_path, "FREE")  # should not raise
