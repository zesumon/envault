"""CLI tests for watcher commands."""
import json
import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.cli_watchers import cmd_watcher


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    vp = tmp_path / "default.vault"
    vp.write_text(json.dumps({"API_KEY": "enc", "DB_PASS": "enc"}))
    return tmp_path


def _invoke(runner, vault_dir, *args):
    from envault import storage
    storage._VAULT_DIR_OVERRIDE = str(vault_dir)
    result = runner.invoke(cmd_watcher, list(args))
    storage._VAULT_DIR_OVERRIDE = None
    return result


def test_watcher_list_empty(runner, vault_dir):
    result = _invoke(runner, vault_dir, "list")
    assert result.exit_code == 0
    assert "No watchers" in result.output


def test_watcher_add_success(runner, vault_dir):
    result = _invoke(runner, vault_dir, "add", "API_KEY", "alice")
    assert result.exit_code == 0
    assert "alice" in result.output


def test_watcher_add_missing_key_fails(runner, vault_dir):
    result = _invoke(runner, vault_dir, "add", "GHOST", "alice")
    assert result.exit_code != 0


def test_watcher_list_by_key(runner, vault_dir):
    _invoke(runner, vault_dir, "add", "API_KEY", "alice")
    result = _invoke(runner, vault_dir, "list", "API_KEY")
    assert "alice" in result.output


def test_watcher_remove(runner, vault_dir):
    _invoke(runner, vault_dir, "add", "API_KEY", "alice")
    result = _invoke(runner, vault_dir, "remove", "API_KEY", "alice")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_watcher_clear(runner, vault_dir):
    _invoke(runner, vault_dir, "add", "API_KEY", "alice")
    _invoke(runner, vault_dir, "add", "API_KEY", "bob")
    result = _invoke(runner, vault_dir, "clear", "API_KEY")
    assert "2" in result.output
