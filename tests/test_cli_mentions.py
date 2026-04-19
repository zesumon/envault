"""Tests for CLI mention commands."""
import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.cli_mentions import cmd_mention
from envault.storage import save_vault


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


def _invoke(runner, vault_dir, args):
    vp = vault_dir / "secrets.vault"
    return runner.invoke(cmd_mention, args + ["--vault", str(vp)])


def _add_key(vault_dir, key, value="val"):
    vp = vault_dir / "secrets.vault"
    from envault.storage import load_vault
    vault = load_vault(vp, "pw")
    vault[key] = value
    save_vault(vp, vault, "pw")


def test_mention_list_empty(runner, vault_dir):
    result = _invoke(runner, vault_dir, ["list"])
    assert result.exit_code == 0
    assert "No mentions" in result.output


def test_mention_add_success(runner, vault_dir):
    _add_key(vault_dir, "DB_URL")
    result = _invoke(runner, vault_dir, ["add", "DB_URL", "APP"])
    assert result.exit_code == 0
    assert "APP" in result.output


def test_mention_add_missing_key_fails(runner, vault_dir):
    result = _invoke(runner, vault_dir, ["add", "MISSING", "APP"])
    assert result.exit_code != 0


def test_mention_list_for_key(runner, vault_dir):
    _add_key(vault_dir, "SECRET")
    _invoke(runner, vault_dir, ["add", "SECRET", "MOD_X"])
    result = _invoke(runner, vault_dir, ["list", "SECRET"])
    assert "MOD_X" in result.output


def test_mention_remove(runner, vault_dir):
    _add_key(vault_dir, "KEY")
    _invoke(runner, vault_dir, ["add", "KEY", "REF"])
    result = _invoke(runner, vault_dir, ["remove", "KEY", "REF"])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_mention_clear(runner, vault_dir):
    _add_key(vault_dir, "KEY")
    _invoke(runner, vault_dir, ["add", "KEY", "R1"])
    _invoke(runner, vault_dir, ["add", "KEY", "R2"])
    result = _invoke(runner, vault_dir, ["clear", "KEY"])
    assert "2" in result.output
