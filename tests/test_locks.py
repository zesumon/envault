import pytest
from pathlib import Path
from envault.locks import lock_key, unlock_key, is_locked, list_locks, assert_not_locked
from envault.storage import save_vault


@pytest.fixture
def vault_path(tmp_path):
    vp = tmp_path / ".envault" / "vault.enc"
    vp.parent.mkdir(parents=True)
    save_vault(vp, {}, "pass")
    return vp


def test_list_locks_empty_when_no_file(vault_path):
    assert list_locks(vault_path) == []


def test_lock_key_and_retrieve(vault_path):
    lock_key(vault_path, "SECRET_KEY")
    assert is_locked(vault_path, "SECRET_KEY")


def test_lock_multiple_keys(vault_path):
    lock_key(vault_path, "KEY_A")
    lock_key(vault_path, "KEY_B")
    locks = list_locks(vault_path)
    assert "KEY_A" in locks
    assert "KEY_B" in locks


def test_lock_duplicate_is_idempotent(vault_path):
    lock_key(vault_path, "MY_KEY")
    lock_key(vault_path, "MY_KEY")
    assert list_locks(vault_path).count("MY_KEY") == 1


def test_unlock_key_returns_true_when_locked(vault_path):
    lock_key(vault_path, "TOKEN")
    result = unlock_key(vault_path, "TOKEN")
    assert result is True
    assert not is_locked(vault_path, "TOKEN")


def test_unlock_key_returns_false_when_not_locked(vault_path):
    result = unlock_key(vault_path, "GHOST")
    assert result is False


def test_is_locked_false_for_unknown_key(vault_path):
    assert not is_locked(vault_path, "UNKNOWN")


def test_assert_not_locked_raises_for_locked_key(vault_path):
    lock_key(vault_path, "DB_PASS")
    with pytest.raises(PermissionError, match="locked"):
        assert_not_locked(vault_path, "DB_PASS")


def test_assert_not_locked_passes_for_unlocked_key(vault_path):
    assert_not_locked(vault_path, "SAFE_KEY")  # should not raise


def test_list_locks_returns_sorted(vault_path):
    lock_key(vault_path, "Z_KEY")
    lock_key(vault_path, "A_KEY")
    locks = list_locks(vault_path)
    assert locks == sorted(locks)
