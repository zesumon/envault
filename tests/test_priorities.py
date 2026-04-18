"""Tests for envault.priorities."""
import pytest
from pathlib import Path
from envault.priorities import (
    set_priority, get_priority, remove_priority,
    list_priorities, keys_by_priority,
)


@pytest.fixture
def vault_path(tmp_path):
    return tmp_path / ".envault" / "vault.enc"


def _set(vault_path, key, priority):
    # bypass storage check by patching load_vault
    import envault.priorities as mod
    orig = mod.__builtins__ if isinstance(mod.__builtins__, dict) else None
    from unittest.mock import patch
    with patch("envault.priorities.load_vault", return_value={}):
        set_priority(vault_path, key, priority)


def test_get_priority_returns_none_when_no_file(vault_path):
    assert get_priority(vault_path, "KEY") is None


def test_set_and_get_priority(vault_path):
    _set(vault_path, "DB_PASS", "high")
    assert get_priority(vault_path, "DB_PASS") == "high"


def test_set_priority_invalid_raises(vault_path):
    from unittest.mock import patch
    with patch("envault.priorities.load_vault", return_value={}):
        with pytest.raises(ValueError, match="Invalid priority"):
            set_priority(vault_path, "KEY", "ultra")


def test_set_priority_overwrites(vault_path):
    _set(vault_path, "API_KEY", "low")
    _set(vault_path, "API_KEY", "critical")
    assert get_priority(vault_path, "API_KEY") == "critical"


def test_remove_priority_returns_true(vault_path):
    _set(vault_path, "X", "medium")
    assert remove_priority(vault_path, "X") is True
    assert get_priority(vault_path, "X") is None


def test_remove_missing_returns_false(vault_path):
    assert remove_priority(vault_path, "MISSING") is False


def test_list_priorities_empty(vault_path):
    assert list_priorities(vault_path) == {}


def test_list_priorities_returns_all(vault_path):
    _set(vault_path, "A", "low")
    _set(vault_path, "B", "high")
    data = list_priorities(vault_path)
    assert data == {"A": "low", "B": "high"}


def test_keys_by_priority(vault_path):
    _set(vault_path, "A", "high")
    _set(vault_path, "B", "low")
    _set(vault_path, "C", "high")
    result = keys_by_priority(vault_path, "high")
    assert result == ["A", "C"]


def test_keys_by_priority_invalid_raises(vault_path):
    with pytest.raises(ValueError):
        keys_by_priority(vault_path, "extreme")
