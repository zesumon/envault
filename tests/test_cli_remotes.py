"""CLI integration tests for remote commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.cli_remotes import cmd_remote


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


def _invoke(runner, vault_dir, *args):
    return runner.invoke(
        cmd_remote,
        list(args),
        obj={"vault_dir": str(vault_dir)},
        catch_exceptions=False,
    )


def test_remote_list_empty(runner, vault_dir):
    result = _invoke(runner, vault_dir, "list")
    assert result.exit_code == 0
    assert "No remotes" in result.output


def test_remote_add_success(runner, vault_dir):
    result = _invoke(runner, vault_dir, "add", "origin", "https://example.com")
    assert result.exit_code == 0
    assert "added" in result.output


def test_remote_add_then_list(runner, vault_dir):
    _invoke(runner, vault_dir, "add", "origin", "https://example.com")
    result = _invoke(runner, vault_dir, "list")
    assert "origin" in result.output
    assert "https://example.com" in result.output


def test_remote_add_duplicate_fails(runner, vault_dir):
    _invoke(runner, vault_dir, "add", "origin", "https://example.com")
    result = _invoke(runner, vault_dir, "add", "origin", "https://other.com")
    assert result.exit_code != 0
    assert "already exists" in result.output


def test_remote_show(runner, vault_dir):
    _invoke(runner, vault_dir, "add", "origin", "https://example.com")
    result = _invoke(runner, vault_dir, "show", "origin")
    assert result.exit_code == 0
    assert "https://example.com" in result.output


def test_remote_show_missing_fails(runner, vault_dir):
    result = _invoke(runner, vault_dir, "show", "ghost")
    assert result.exit_code != 0


def test_remote_update(runner, vault_dir):
    _invoke(runner, vault_dir, "add", "origin", "https://old.example.com")
    result = _invoke(runner, vault_dir, "update", "origin", "https://new.example.com")
    assert result.exit_code == 0
    assert "updated" in result.output
    show = _invoke(runner, vault_dir, "show", "origin")
    assert "https://new.example.com" in show.output


def test_remote_remove(runner, vault_dir):
    _invoke(runner, vault_dir, "add", "origin", "https://example.com")
    result = _invoke(runner, vault_dir, "remove", "origin")
    assert result.exit_code == 0
    assert "removed" in result.output
    list_result = _invoke(runner, vault_dir, "list")
    assert "No remotes" in list_result.output
