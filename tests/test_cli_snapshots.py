"""CLI tests for snapshot commands."""

import pytest
from click.testing import CliRunner

from envault.cli_snapshots import cmd_snapshot
from envault.storage import set_secret


PASSWORD = "cli-snap-pass"


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def _invoke(runner, vault_dir, args, input_text=None):
    full_args = args + ["--vault-dir", vault_dir]
    return runner.invoke(cmd_snapshot, full_args, input=input_text, catch_exceptions=False)


def test_snapshot_list_empty(runner, vault_dir):
    result = _invoke(runner, vault_dir, ["list"])
    assert result.exit_code == 0
    assert "No snapshots" in result.output


def test_snapshot_create_and_list(runner, vault_dir):
    set_secret("FOO", "bar", PASSWORD, vault_dir=vault_dir)
    result = _invoke(runner, vault_dir, ["create", "--name", "mysnap"], input_text=PASSWORD + "\n")
    assert result.exit_code == 0
    assert "mysnap" in result.output

    result = _invoke(runner, vault_dir, ["list"])
    assert "mysnap" in result.output


def test_snapshot_create_duplicate_fails(runner, vault_dir):
    set_secret("X", "y", PASSWORD, vault_dir=vault_dir)
    _invoke(runner, vault_dir, ["create", "--name", "dup"], input_text=PASSWORD + "\n")
    result = _invoke(runner, vault_dir, ["create", "--name", "dup"], input_text=PASSWORD + "\n")
    assert result.exit_code != 0


def test_snapshot_restore(runner, vault_dir):
    set_secret("MYKEY", "original", PASSWORD, vault_dir=vault_dir)
    _invoke(runner, vault_dir, ["create", "--name", "snap1"], input_text=PASSWORD + "\n")

    set_secret("MYKEY", "changed", PASSWORD, vault_dir=vault_dir)

    result = _invoke(runner, vault_dir, ["restore", "snap1"], input_text=PASSWORD + "\n")
    assert result.exit_code == 0
    assert "Restored" in result.output


def test_snapshot_restore_missing(runner, vault_dir):
    result = _invoke(runner, vault_dir, ["restore", "ghost"], input_text=PASSWORD + "\n")
    assert result.exit_code != 0


def test_snapshot_delete(runner, vault_dir):
    set_secret("K", "v", PASSWORD, vault_dir=vault_dir)
    _invoke(runner, vault_dir, ["create", "--name", "delme"], input_text=PASSWORD + "\n")
    result = _invoke(runner, vault_dir, ["delete", "delme"])
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_snapshot_delete_missing(runner, vault_dir):
    result = _invoke(runner, vault_dir, ["delete", "nope"])
    assert result.exit_code != 0
