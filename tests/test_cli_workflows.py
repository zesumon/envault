import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch
from envault.cli_workflows import cmd_workflow


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


def _invoke(runner, vault_dir, *args):
    vault_path = str(vault_dir / "vault.db")
    with patch("envault.cli_workflows.get_vault_path", return_value=vault_path):
        return runner.invoke(cmd_workflow, list(args))


def test_workflow_list_empty(runner, vault_dir):
    result = _invoke(runner, vault_dir, "list")
    assert result.exit_code == 0
    assert "No workflows" in result.output


def test_workflow_save_and_list(runner, vault_dir):
    _invoke(runner, vault_dir, "save", "deploy", "export", "sync")
    result = _invoke(runner, vault_dir, "list")
    assert "deploy" in result.output


def test_workflow_show_steps(runner, vault_dir):
    _invoke(runner, vault_dir, "save", "setup", "init", "import")
    result = _invoke(runner, vault_dir, "show", "setup")
    assert "init" in result.output
    assert "import" in result.output


def test_workflow_show_missing(runner, vault_dir):
    result = _invoke(runner, vault_dir, "show", "ghost")
    assert result.exit_code != 0


def test_workflow_delete(runner, vault_dir):
    _invoke(runner, vault_dir, "save", "tmp", "x")
    result = _invoke(runner, vault_dir, "delete", "tmp")
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_workflow_rename(runner, vault_dir):
    _invoke(runner, vault_dir, "save", "old", "step")
    result = _invoke(runner, vault_dir, "rename", "old", "new")
    assert result.exit_code == 0
    r2 = _invoke(runner, vault_dir, "list")
    assert "new" in r2.output
    assert "old" not in r2.output
