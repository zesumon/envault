"""Tests for the trigger CLI commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.cli_triggers import cmd_trigger


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_dir(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    return tmp_path


def _invoke(runner, vault_dir, *args):
    return runner.invoke(cmd_trigger, list(args), catch_exceptions=False)


def test_trigger_list_empty(runner, vault_dir):
    result = _invoke(runner, vault_dir, "list")
    assert result.exit_code == 0
    assert "No triggers" in result.output


def test_trigger_add_success(runner, vault_dir):
    result = _invoke(runner, vault_dir, "add", "API_KEY", "on_set", "echo hello")
    assert result.exit_code == 0
    assert "Trigger added" in result.output


def test_trigger_list_shows_added(runner, vault_dir):
    _invoke(runner, vault_dir, "add", "API_KEY", "on_set", "echo hello")
    result = _invoke(runner, vault_dir, "list")
    assert "API_KEY" in result.output
    assert "on_set" in result.output
    assert "echo hello" in result.output


def test_trigger_add_invalid_event(runner, vault_dir):
    result = runner.invoke(cmd_trigger, ["add", "KEY", "on_magic", "cmd"])
    assert result.exit_code != 0
    assert "Invalid event" in result.output


def test_trigger_remove_success(runner, vault_dir):
    _invoke(runner, vault_dir, "add", "DB_URL", "on_delete", "cleanup.sh")
    result = _invoke(runner, vault_dir, "remove", "DB_URL", "on_delete", "cleanup.sh")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_trigger_remove_missing(runner, vault_dir):
    result = _invoke(runner, vault_dir, "remove", "GHOST", "on_set", "cmd")
    assert result.exit_code == 0
    assert "not found" in result.output


def test_trigger_clear(runner, vault_dir):
    _invoke(runner, vault_dir, "add", "TOKEN", "on_set", "a")
    _invoke(runner, vault_dir, "add", "TOKEN", "on_expire", "b")
    result = _invoke(runner, vault_dir, "clear", "TOKEN")
    assert result.exit_code == 0
    assert "cleared" in result.output


def test_trigger_events_lists_valid(runner, vault_dir):
    result = _invoke(runner, vault_dir, "events")
    assert result.exit_code == 0
    assert "on_set" in result.output
    assert "on_delete" in result.output
