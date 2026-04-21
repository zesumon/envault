"""Tests for envault.lifecycle module."""

import pytest
from pathlib import Path

from envault.lifecycle import (
    VALID_STATES,
    get_lifecycle,
    keys_by_state,
    list_lifecycle,
    remove_lifecycle,
    set_lifecycle,
)


@pytest.fixture
def vault_path(tmp_path):
    return tmp_path / "vault.enc"


def test_get_lifecycle_returns_none_when_no_file(vault_path):
    assert get_lifecycle(vault_path, "MY_KEY") is None


def test_set_and_get_lifecycle(vault_path):
    set_lifecycle(vault_path, "MY_KEY", "active")
    assert get_lifecycle(vault_path, "MY_KEY") == "active"


def test_set_lifecycle_invalid_state_raises(vault_path):
    with pytest.raises(ValueError, match="Invalid state"):
        set_lifecycle(vault_path, "MY_KEY", "unknown")


def test_set_lifecycle_overwrites(vault_path):
    set_lifecycle(vault_path, "MY_KEY", "draft")
    set_lifecycle(vault_path, "MY_KEY", "deprecated")
    assert get_lifecycle(vault_path, "MY_KEY") == "deprecated"


def test_remove_lifecycle_returns_true_when_existed(vault_path):
    set_lifecycle(vault_path, "MY_KEY", "archived")
    result = remove_lifecycle(vault_path, "MY_KEY")
    assert result is True
    assert get_lifecycle(vault_path, "MY_KEY") is None


def test_remove_lifecycle_returns_false_when_missing(vault_path):
    result = remove_lifecycle(vault_path, "NONEXISTENT")
    assert result is False


def test_list_lifecycle_empty_when_no_file(vault_path):
    assert list_lifecycle(vault_path) == {}


def test_list_lifecycle_returns_sorted(vault_path):
    set_lifecycle(vault_path, "Z_KEY", "active")
    set_lifecycle(vault_path, "A_KEY", "deprecated")
    set_lifecycle(vault_path, "M_KEY", "draft")
    result = list_lifecycle(vault_path)
    assert list(result.keys()) == ["A_KEY", "M_KEY", "Z_KEY"]


def test_keys_by_state_returns_matching(vault_path):
    set_lifecycle(vault_path, "KEY_A", "active")
    set_lifecycle(vault_path, "KEY_B", "deprecated")
    set_lifecycle(vault_path, "KEY_C", "active")
    result = keys_by_state(vault_path, "active")
    assert result == ["KEY_A", "KEY_C"]


def test_keys_by_state_empty_when_none_match(vault_path):
    set_lifecycle(vault_path, "KEY_A", "active")
    result = keys_by_state(vault_path, "archived")
    assert result == []


def test_keys_by_state_invalid_raises(vault_path):
    with pytest.raises(ValueError, match="Invalid state"):
        keys_by_state(vault_path, "bogus")


def test_all_valid_states_accepted(vault_path):
    for i, state in enumerate(VALID_STATES):
        set_lifecycle(vault_path, f"KEY_{i}", state)
        assert get_lifecycle(vault_path, f"KEY_{i}") == state
