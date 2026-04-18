import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch
from envault.cli_schema import cmd_schema
from envault.storage import save_vault
from envault import schema as sc


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


def _invoke(runner, vault_dir, args, password="pass"):
    vp = vault_dir / "vault.enc"
    with patch("envault.storage.get_vault_path", return_value=vp):
        with patch("envault.cli_schema.get_vault_path", return_value=vp):
            return runner.invoke(cmd_schema, args, catch_exceptions=False)


def test_schema_list_empty(runner, vault_dir):
    result = _invoke(runner, vault_dir, ["list"])
    assert result.exit_code == 0
    assert "No schema rules" in result.output


def test_schema_set_and_list(runner, vault_dir):
    _invoke(runner, vault_dir, ["set", "PORT", "--type", "integer"])
    result = _invoke(runner, vault_dir, ["list"])
    assert "PORT" in result.output
    assert "integer" in result.output


def test_schema_set_required(runner, vault_dir):
    result = _invoke(runner, vault_dir, ["set", "API_KEY", "--type", "string", "--required"])
    assert result.exit_code == 0
    assert "required=True" in result.output


def test_schema_remove(runner, vault_dir):
    _invoke(runner, vault_dir, ["set", "HOST", "--type", "string"])
    result = _invoke(runner, vault_dir, ["remove", "HOST"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_schema_remove_missing(runner, vault_dir):
    result = _invoke(runner, vault_dir, ["remove", "GHOST"])
    assert result.exit_code == 0
    assert "No schema rule" in result.output


def test_schema_check_passes(runner, vault_dir):
    vp = vault_dir / "vault.enc"
    save_vault(vp, {"PORT": "8080"}, "pass")
    sc.set_schema(vp, "PORT", "integer")
    with patch("envault.cli_schema.get_vault_path", return_value=vp):
        with patch("envault.cli_schema._get_password", return_value="pass"):
            result = runner.invoke(cmd_schema, ["check", "--password", "pass"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "pass" in result.output


def test_schema_check_fails_on_bad_value(runner, vault_dir):
    vp = vault_dir / "vault.enc"
    save_vault(vp, {"PORT": "not-a-number"}, "pass")
    sc.set_schema(vp, "PORT", "integer")
    with patch("envault.cli_schema.get_vault_path", return_value=vp):
        with patch("envault.cli_schema._get_password", return_value="pass"):
            result = runner.invoke(cmd_schema, ["check", "--password", "pass"])
    assert result.exit_code != 0
