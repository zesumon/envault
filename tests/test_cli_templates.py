"""Tests for CLI template commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.cli_templates import cmd_template
from envault.storage import save_vault


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    d = tmp_path / ".envault"
    d.mkdir()
    return d


def _invoke(runner, vault_dir, *args, **kwargs):
    extra = ["--vault-dir", str(vault_dir)]
    return runner.invoke(cmd_template, list(args) + extra, **kwargs)


def test_template_list_empty(runner, vault_dir):
    result = _invoke(runner, vault_dir, "list")
    assert result.exit_code == 0
    assert "No templates" in result.output


def test_template_save_and_list(runner, vault_dir):
    result = _invoke(runner, vault_dir, "save", "myapp", "DB_URL", "SECRET")
    assert result.exit_code == 0
    assert "saved" in result.output

    result = _invoke(runner, vault_dir, "list")
    assert "myapp" in result.output
    assert "DB_URL" in result.output


def test_template_save_invalid_name(runner, vault_dir):
    result = _invoke(runner, vault_dir, "save", "bad name", "KEY")
    assert result.exit_code != 0
    assert "Invalid" in result.output


def test_template_delete(runner, vault_dir):
    _invoke(runner, vault_dir, "save", "tmp", "X")
    result = _invoke(runner, vault_dir, "delete", "tmp")
    assert result.exit_code == 0
    assert "deleted" in result.output

    result = _invoke(runner, vault_dir, "list")
    assert "tmp" not in result.output


def test_template_delete_missing(runner, vault_dir):
    result = _invoke(runner, vault_dir, "delete", "ghost")
    assert result.exit_code != 0


def test_template_check_all_present(runner, vault_dir):
    password = "pw"
    vault_file = vault_dir / "vault.enc"
    save_vault(vault_file, {"DB_URL": "postgres://", "SECRET": "abc"}, password)
    _invoke(runner, vault_dir, "save", "app", "DB_URL", "SECRET")
    result = runner.invoke(
        cmd_template,
        ["check", "app", "--password", password, "--vault-dir", str(vault_dir)],
    )
    assert result.exit_code == 0
    assert "All keys" in result.output


def test_template_check_missing_keys(runner, vault_dir):
    password = "pw"
    vault_file = vault_dir / "vault.enc"
    save_vault(vault_file, {"DB_URL": "postgres://"}, password)
    _invoke(runner, vault_dir, "save", "app", "DB_URL", "SECRET", "TOKEN")
    result = runner.invoke(
        cmd_template,
        ["check", "app", "--password", password, "--vault-dir", str(vault_dir)],
    )
    assert result.exit_code == 0
    assert "SECRET" in result.output
    assert "TOKEN" in result.output
