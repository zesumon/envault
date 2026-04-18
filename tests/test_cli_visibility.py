import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.cli_visibility import cmd_visibility


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


def _invoke(runner, vault_dir, *args):
    vault = str(vault_dir / "vault.enc")
    return runner.invoke(cmd_visibility, list(args) + ["--vault", vault])


def test_visibility_list_empty(runner, vault_dir):
    result = _invoke(runner, vault_dir, "list")
    assert result.exit_code == 0
    assert "No visibility" in result.output


def test_visibility_set_and_get(runner, vault_dir):
    result = _invoke(runner, vault_dir, "set", "API_KEY", "private")
    assert result.exit_code == 0
    assert "private" in result.output

    result = _invoke(runner, vault_dir, "get", "API_KEY")
    assert result.exit_code == 0
    assert "private" in result.output


def test_visibility_get_missing(runner, vault_dir):
    result = _invoke(runner, vault_dir, "get", "MISSING")
    assert result.exit_code == 0
    assert "defaults to public" in result.output


def test_visibility_remove(runner, vault_dir):
    _invoke(runner, vault_dir, "set", "TOKEN", "masked")
    result = _invoke(runner, vault_dir, "remove", "TOKEN")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_visibility_remove_missing(runner, vault_dir):
    result = _invoke(runner, vault_dir, "remove", "GHOST")
    assert result.exit_code == 0
    assert "No visibility setting found" in result.output


def test_visibility_list_shows_entries(runner, vault_dir):
    _invoke(runner, vault_dir, "set", "KEY1", "public")
    _invoke(runner, vault_dir, "set", "KEY2", "private")
    result = _invoke(runner, vault_dir, "list")
    assert "KEY1" in result.output
    assert "KEY2" in result.output
