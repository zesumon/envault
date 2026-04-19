"""Tests for envault.mentions."""
import pytest
from pathlib import Path
from envault.mentions import add_mention, remove_mention, get_mentions, list_all_mentions, clear_mentions
from envault.storage import save_vault


@pytest.fixture
def vault_path(tmp_path):
    vp = tmp_path / "vault" / "secrets.vault"
    vp.parent.mkdir(parents=True)
    return vp


def _add_key(vault_path, key, value="val"):
    from envault.storage import load_vault
    vault = load_vault(vault_path, "pw")
    vault[key] = value
    save_vault(vault_path, vault, "pw")


def test_get_mentions_empty_when_no_file(vault_path):
    _add_key(vault_path, "DB_URL")
    assert get_mentions(vault_path, "DB_URL") == []


def test_add_mention_and_retrieve(vault_path):
    _add_key(vault_path, "DB_URL")
    add_mention(vault_path, "DB_URL", "APP_CONFIG")
    assert "APP_CONFIG" in get_mentions(vault_path, "DB_URL")


def test_add_duplicate_mention_is_idempotent(vault_path):
    _add_key(vault_path, "DB_URL")
    add_mention(vault_path, "DB_URL", "APP_CONFIG")
    add_mention(vault_path, "DB_URL", "APP_CONFIG")
    assert get_mentions(vault_path, "DB_URL").count("APP_CONFIG") == 1


def test_add_mention_missing_key_raises(vault_path):
    with pytest.raises(KeyError):
        add_mention(vault_path, "MISSING", "OTHER")


def test_add_multiple_mentioners(vault_path):
    _add_key(vault_path, "SECRET")
    add_mention(vault_path, "SECRET", "MOD_A")
    add_mention(vault_path, "SECRET", "MOD_B")
    refs = get_mentions(vault_path, "SECRET")
    assert "MOD_A" in refs
    assert "MOD_B" in refs


def test_remove_mention_returns_true(vault_path):
    _add_key(vault_path, "KEY")
    add_mention(vault_path, "KEY", "REF")
    assert remove_mention(vault_path, "KEY", "REF") is True
    assert get_mentions(vault_path, "KEY") == []


def test_remove_nonexistent_mention_returns_false(vault_path):
    _add_key(vault_path, "KEY")
    assert remove_mention(vault_path, "KEY", "NOBODY") is False


def test_list_all_mentions(vault_path):
    _add_key(vault_path, "A")
    _add_key(vault_path, "B")
    add_mention(vault_path, "A", "X")
    add_mention(vault_path, "B", "Y")
    data = list_all_mentions(vault_path)
    assert "A" in data
    assert "B" in data


def test_clear_mentions_returns_count(vault_path):
    _add_key(vault_path, "KEY")
    add_mention(vault_path, "KEY", "R1")
    add_mention(vault_path, "KEY", "R2")
    assert clear_mentions(vault_path, "KEY") == 2
    assert get_mentions(vault_path, "KEY") == []


def test_clear_mentions_key_not_present_returns_zero(vault_path):
    assert clear_mentions(vault_path, "GHOST") == 0
