"""Tests for envault CLI hook commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.cli_hooks import cmd_hook


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


def _invoke(runner, vault_dir, *args):
    return runner.invoke(cmd_hook, ["--vault-dir", str(vault_dir), *args])


def test_hook_list_empty(runner, vault_dir):
    result = _invoke(runner, vault_dir, "list")
    assert result.exit_code == 0
    assert "No hooks registered" in result.output


def test_hook_add_success(runner, vault_dir):
    result = _invoke(runner, vault_dir, "add", "post-set", "echo hello")
    assert result.exit_code == 0
    assert "Hook added" in result.output


def test_hook_add_then_list(runner, vault_dir):
    _invoke(runner, vault_dir, "add", "post-set", "make test")
    result = _invoke(runner, vault_dir, "list")
    assert "post-set" in result.output
    assert "make test" in result.output


def test_hook_add_invalid_event(runner, vault_dir):
    result = _invoke(runner, vault_dir, "add", "on-magic", "echo nope")
    assert result.exit_code != 0
    assert "Error" in result.output


def test_hook_add_duplicate_fails(runner, vault_dir):
    _invoke(runner, vault_dir, "add", "pre-delete", "echo bye")
    result = _invoke(runner, vault_dir, "add", "pre-delete", "echo bye")
    assert result.exit_code != 0
    assert "Error" in result.output


def test_hook_remove_success(runner, vault_dir):
    _invoke(runner, vault_dir, "add", "post-export", "notify done")
    result = _invoke(runner, vault_dir, "remove", "post-export", "notify done")
    assert result.exit_code == 0
    assert "Hook removed" in result.output


def test_hook_remove_missing_fails(runner, vault_dir):
    result = _invoke(runner, vault_dir, "remove", "post-set", "ghost-cmd")
    assert result.exit_code != 0


def test_hook_events_lists_all(runner, vault_dir):
    result = runner.invoke(cmd_hook, ["events"])
    assert result.exit_code == 0
    assert "post-set" in result.output
    assert "pre-delete" in result.output
