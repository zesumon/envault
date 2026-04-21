"""Tests for envault.cli_constraints."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.cli_constraints import cmd_constraint


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_VAULT_DIR", str(tmp_path))
    return tmp_path


def _invoke(runner, vault_dir, *args):
    return runner.invoke(cmd_constraint, list(args), catch_exceptions=False)


def test_constraint_list_empty(runner, vault_dir):
    result = _invoke(runner, vault_dir, "list")
    assert result.exit_code == 0
    assert "No constraints" in result.output


def test_constraint_set_and_list(runner, vault_dir):
    r = _invoke(runner, vault_dir, "set", "API_KEY", "min_length", "16")
    assert r.exit_code == 0
    assert "set" in r.output

    r2 = _invoke(runner, vault_dir, "list")
    assert "API_KEY" in r2.output
    assert "min_length=16" in r2.output


def test_constraint_set_invalid_type(runner, vault_dir):
    r = runner.invoke(cmd_constraint, ["set", "KEY", "badtype", "val"])
    assert r.exit_code != 0


def test_constraint_remove(runner, vault_dir):
    _invoke(runner, vault_dir, "set", "TOKEN", "max_length", "32")
    r = _invoke(runner, vault_dir, "remove", "TOKEN", "max_length")
    assert r.exit_code == 0
    assert "removed" in r.output


def test_constraint_remove_missing(runner, vault_dir):
    r = _invoke(runner, vault_dir, "remove", "GHOST", "regex")
    assert r.exit_code == 0
    assert "No constraint" in r.output


def test_constraint_check_pass(runner, vault_dir):
    _invoke(runner, vault_dir, "set", "K", "min_length", "3")
    r = _invoke(runner, vault_dir, "check", "K", "hello")
    assert r.exit_code == 0
    assert "OK" in r.output


def test_constraint_check_fail(runner, vault_dir):
    _invoke(runner, vault_dir, "set", "K", "min_length", "20")
    r = runner.invoke(cmd_constraint, ["check", "K", "short"], catch_exceptions=False)
    assert r.exit_code != 0
    assert "FAIL" in r.output


def test_constraint_list_by_key(runner, vault_dir):
    _invoke(runner, vault_dir, "set", "A", "min_length", "5")
    _invoke(runner, vault_dir, "set", "B", "max_length", "10")
    r = _invoke(runner, vault_dir, "list", "A")
    assert "A" in r.output
    assert "B" not in r.output
