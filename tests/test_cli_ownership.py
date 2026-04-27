"""Tests for the ownership CLI commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_ownership import cmd_ownership


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


def _invoke(runner, vault_dir, *args):
    vault_path = str(vault_dir / "vault.enc")
    return runner.invoke(cmd_ownership, list(args) + ["--vault", vault_path])


def test_ownership_list_empty(runner, vault_dir):
    result = _invoke(runner, vault_dir, "list")
    assert result.exit_code == 0
    assert "No ownership records" in result.output


def test_ownership_set_success(runner, vault_dir):
    result = _invoke(runner, vault_dir, "set", "API_KEY", "alice")
    assert result.exit_code == 0
    assert "alice" in result.output


def test_ownership_get_after_set(runner, vault_dir):
    _invoke(runner, vault_dir, "set", "API_KEY", "alice")
    result = _invoke(runner, vault_dir, "get", "API_KEY")
    assert result.exit_code == 0
    assert "alice" in result.output


def test_ownership_get_unset_key(runner, vault_dir):
    result = _invoke(runner, vault_dir, "get", "MISSING")
    assert result.exit_code == 0
    assert "No owner" in result.output


def test_ownership_remove_existing(runner, vault_dir):
    _invoke(runner, vault_dir, "set", "API_KEY", "alice")
    result = _invoke(runner, vault_dir, "remove", "API_KEY")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_ownership_remove_missing(runner, vault_dir):
    result = _invoke(runner, vault_dir, "remove", "GHOST_KEY")
    assert result.exit_code == 0
    assert "No ownership record found" in result.output


def test_ownership_list_filter_by_owner(runner, vault_dir):
    _invoke(runner, vault_dir, "set", "A", "alice")
    _invoke(runner, vault_dir, "set", "B", "bob")
    result = _invoke(runner, vault_dir, "list", "--owner", "alice")
    assert result.exit_code == 0
    assert "A" in result.output
    assert "B" not in result.output


def test_ownership_list_shows_all(runner, vault_dir):
    _invoke(runner, vault_dir, "set", "X", "alice")
    _invoke(runner, vault_dir, "set", "Y", "bob")
    result = _invoke(runner, vault_dir, "list")
    assert result.exit_code == 0
    assert "alice" in result.output
    assert "bob" in result.output
