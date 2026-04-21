"""Tests for envault.constraints."""

import pytest
from pathlib import Path

from envault.constraints import (
    set_constraint,
    remove_constraint,
    get_constraints,
    list_constraints,
    validate_value,
)


@pytest.fixture
def vault_path(tmp_path):
    return tmp_path / "vault.db"


def test_get_constraints_empty_when_no_file(vault_path):
    assert get_constraints(vault_path, "API_KEY") == {}


def test_list_constraints_empty_when_no_file(vault_path):
    assert list_constraints(vault_path) == {}


def test_set_and_get_constraint(vault_path):
    set_constraint(vault_path, "API_KEY", "min_length", "16")
    c = get_constraints(vault_path, "API_KEY")
    assert c["min_length"] == "16"


def test_set_multiple_constraints_same_key(vault_path):
    set_constraint(vault_path, "TOKEN", "min_length", "8")
    set_constraint(vault_path, "TOKEN", "max_length", "64")
    set_constraint(vault_path, "TOKEN", "regex", r"[A-Za-z0-9]+")
    c = get_constraints(vault_path, "TOKEN")
    assert len(c) == 3


def test_set_constraint_invalid_type_raises(vault_path):
    with pytest.raises(ValueError, match="Invalid constraint type"):
        set_constraint(vault_path, "KEY", "nonexistent", "value")


def test_set_min_length_non_integer_raises(vault_path):
    with pytest.raises(ValueError, match="must be an integer"):
        set_constraint(vault_path, "KEY", "min_length", "abc")


def test_remove_constraint_returns_true(vault_path):
    set_constraint(vault_path, "KEY", "min_length", "4")
    result = remove_constraint(vault_path, "KEY", "min_length")
    assert result is True
    assert get_constraints(vault_path, "KEY") == {}


def test_remove_constraint_missing_returns_false(vault_path):
    result = remove_constraint(vault_path, "KEY", "regex")
    assert result is False


def test_remove_last_constraint_cleans_up_key(vault_path):
    set_constraint(vault_path, "KEY", "max_length", "10")
    remove_constraint(vault_path, "KEY", "max_length")
    assert "KEY" not in list_constraints(vault_path)


def test_validate_value_passes_all(vault_path):
    set_constraint(vault_path, "PWD", "min_length", "6")
    set_constraint(vault_path, "PWD", "max_length", "20")
    set_constraint(vault_path, "PWD", "regex", r"[A-Za-z0-9!@#]+")
    errors = validate_value(vault_path, "PWD", "Hello1!")
    assert errors == []


def test_validate_value_fails_min_length(vault_path):
    set_constraint(vault_path, "K", "min_length", "10")
    errors = validate_value(vault_path, "K", "short")
    assert any("too short" in e for e in errors)


def test_validate_value_fails_max_length(vault_path):
    set_constraint(vault_path, "K", "max_length", "3")
    errors = validate_value(vault_path, "K", "toolongvalue")
    assert any("too long" in e for e in errors)


def test_validate_value_fails_regex(vault_path):
    set_constraint(vault_path, "K", "regex", r"\d+")
    errors = validate_value(vault_path, "K", "notdigits")
    assert any("pattern" in e for e in errors)


def test_validate_value_no_constraints_is_ok(vault_path):
    errors = validate_value(vault_path, "UNCONSTRAINED", "anything")
    assert errors == []
