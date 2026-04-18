import pytest
from pathlib import Path
from envault.checksums import (
    record_checksum,
    get_checksum,
    remove_checksum,
    verify_checksum,
    verify_all,
)
from envault.storage import save_vault, set_secret


@pytest.fixture
def vault_path(tmp_path):
    return tmp_path / ".envault" / "vault.enc"


def test_get_checksum_returns_none_when_no_file(vault_path):
    assert get_checksum(vault_path, "KEY") is None


def test_record_checksum_returns_hex_string(vault_path):
    digest = record_checksum(vault_path, "API_KEY", "supersecret")
    assert isinstance(digest, str)
    assert len(digest) == 64


def test_get_checksum_after_record(vault_path):
    record_checksum(vault_path, "API_KEY", "supersecret")
    stored = get_checksum(vault_path, "API_KEY")
    assert stored is not None
    assert len(stored) == 64


def test_verify_checksum_correct_value(vault_path):
    record_checksum(vault_path, "TOKEN", "abc123")
    assert verify_checksum(vault_path, "TOKEN", "abc123") is True


def test_verify_checksum_wrong_value(vault_path):
    record_checksum(vault_path, "TOKEN", "abc123")
    assert verify_checksum(vault_path, "TOKEN", "wrongvalue") is False


def test_verify_checksum_missing_key_returns_false(vault_path):
    assert verify_checksum(vault_path, "MISSING", "value") is False


def test_remove_checksum(vault_path):
    record_checksum(vault_path, "KEY", "val")
    remove_checksum(vault_path, "KEY")
    assert get_checksum(vault_path, "KEY") is None


def test_remove_missing_key_is_safe(vault_path):
    remove_checksum(vault_path, "NONEXISTENT")


def test_verify_all_matches(vault_path):
    password = "testpass"
    vault_path.parent.mkdir(parents=True, exist_ok=True)
    set_secret(vault_path, "DB_URL", "postgres://localhost", password)
    record_checksum(vault_path, "DB_URL", "postgres://localhost")
    results = verify_all(vault_path, password)
    assert results["DB_URL"] is True


def test_verify_all_detects_mismatch(vault_path):
    password = "testpass"
    vault_path.parent.mkdir(parents=True, exist_ok=True)
    set_secret(vault_path, "DB_URL", "postgres://localhost", password)
    record_checksum(vault_path, "DB_URL", "old_value")
    results = verify_all(vault_path, password)
    assert results["DB_URL"] is False
