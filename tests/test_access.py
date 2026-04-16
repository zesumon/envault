"""Tests for envault.access module."""
import pytest
from pathlib import Path
from envault import access as acc


@pytest.fixture
def vault_path(tmp_path):
    return tmp_path / "vault" / "secrets.db"


def test_get_access_returns_none_when_no_file(vault_path):
    assert acc.get_access(vault_path, "dev", "API_KEY") is None


def test_set_and_get_access(vault_path):
    acc.set_access(vault_path, "dev", "API_KEY", ["read"])
    assert acc.get_access(vault_path, "dev", "API_KEY") == ["read"]


def test_set_access_both_modes(vault_path):
    acc.set_access(vault_path, "dev", "DB_PASS", ["read", "write"])
    result = acc.get_access(vault_path, "dev", "DB_PASS")
    assert sorted(result) == ["read", "write"]


def test_set_access_invalid_mode_raises(vault_path):
    with pytest.raises(ValueError, match="Invalid modes"):
        acc.set_access(vault_path, "dev", "KEY", ["execute"])


def test_can_read_no_restriction(vault_path):
    assert acc.can_read(vault_path, "dev", "ANYTHING") is True


def test_can_write_no_restriction(vault_path):
    assert acc.can_write(vault_path, "dev", "ANYTHING") is True


def test_can_read_only_mode(vault_path):
    acc.set_access(vault_path, "ci", "SECRET", ["read"])
    assert acc.can_read(vault_path, "ci", "SECRET") is True
    assert acc.can_write(vault_path, "ci", "SECRET") is False


def test_can_write_only_mode(vault_path):
    acc.set_access(vault_path, "admin", "SECRET", ["write"])
    assert acc.can_read(vault_path, "admin", "SECRET") is False
    assert acc.can_write(vault_path, "admin", "SECRET") is True


def test_remove_access(vault_path):
    acc.set_access(vault_path, "dev", "KEY", ["read"])
    acc.remove_access(vault_path, "dev", "KEY")
    assert acc.get_access(vault_path, "dev", "KEY") is None


def test_remove_access_cleans_empty_profile(vault_path):
    acc.set_access(vault_path, "dev", "ONLY_KEY", ["read"])
    acc.remove_access(vault_path, "dev", "ONLY_KEY")
    data = acc._load_access(vault_path)
    assert "dev" not in data


def test_list_access_returns_rules(vault_path):
    acc.set_access(vault_path, "dev", "A", ["read"])
    acc.set_access(vault_path, "dev", "B", ["read", "write"])
    rules = acc.list_access(vault_path, "dev")
    assert "A" in rules
    assert "B" in rules


def test_list_access_empty_for_unknown_profile(vault_path):
    assert acc.list_access(vault_path, "ghost") == {}
