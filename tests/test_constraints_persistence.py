"""Persistence tests for envault.constraints."""

import json
import pytest
from pathlib import Path

from envault.constraints import (
    set_constraint,
    remove_constraint,
    list_constraints,
    _get_constraints_path,
)


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


@pytest.fixture
def vault_path(vault_dir):
    return vault_dir / "vault.db"


def test_constraints_file_is_valid_json(vault_path):
    set_constraint(vault_path, "KEY", "min_length", "8")
    p = _get_constraints_path(vault_path)
    data = json.loads(p.read_text())
    assert isinstance(data, dict)


def test_multiple_constraints_persist(vault_path):
    set_constraint(vault_path, "A", "min_length", "4")
    set_constraint(vault_path, "B", "regex", r"\w+")
    set_constraint(vault_path, "C", "max_length", "50")
    data = list_constraints(vault_path)
    assert "A" in data
    assert "B" in data
    assert "C" in data


def test_overwrite_updates_value(vault_path):
    set_constraint(vault_path, "KEY", "min_length", "4")
    set_constraint(vault_path, "KEY", "min_length", "12")
    data = list_constraints(vault_path)
    assert data["KEY"]["min_length"] == "12"


def test_remove_leaves_others_intact(vault_path):
    set_constraint(vault_path, "KEY", "min_length", "4")
    set_constraint(vault_path, "KEY", "max_length", "100")
    remove_constraint(vault_path, "KEY", "min_length")
    data = list_constraints(vault_path)
    assert "min_length" not in data["KEY"]
    assert "max_length" in data["KEY"]


def test_file_sorted_keys(vault_path):
    set_constraint(vault_path, "Z_KEY", "min_length", "1")
    set_constraint(vault_path, "A_KEY", "min_length", "1")
    p = _get_constraints_path(vault_path)
    raw = p.read_text()
    a_pos = raw.index("A_KEY")
    z_pos = raw.index("Z_KEY")
    assert a_pos < z_pos
