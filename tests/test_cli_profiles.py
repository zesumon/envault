"""Tests for envault.cli_profiles CLI commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch

from envault.cli_profiles import cmd_profile
from envault.profiles import DEFAULT_PROFILE


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


def _invoke(runner, args, vault_dir):
    with patch("envault.profiles.get_vault_path", return_value=vault_dir / "vault.enc"), \
         patch("envault.cli_profiles.log_event"):
        return runner.invoke(cmd_profile, args)


def test_profile_list_shows_default(runner, vault_dir):
    result = _invoke(runner, ["list"], vault_dir)
    assert result.exit_code == 0
    assert DEFAULT_PROFILE in result.output
    assert "(default)" in result.output


def test_profile_create_success(runner, vault_dir):
    result = _invoke(runner, ["create", "staging"], vault_dir)
    assert result.exit_code == 0
    assert "created" in result.output


def test_profile_create_invalid_name(runner, vault_dir):
    result = _invoke(runner, ["create", "bad-name"], vault_dir)
    assert result.exit_code != 0
    assert "Invalid profile name" in result.output


def test_profile_create_duplicate(runner, vault_dir):
    _invoke(runner, ["create", "prod"], vault_dir)
    result = _invoke(runner, ["create", "prod"], vault_dir)
    assert result.exit_code != 0
    assert "already exists" in result.output


def test_profile_delete_with_yes_flag(runner, vault_dir):
    _invoke(runner, ["create", "temp"], vault_dir)
    result = _invoke(runner, ["delete", "temp", "--yes"], vault_dir)
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_profile_delete_default_fails(runner, vault_dir):
    result = _invoke(runner, ["delete", DEFAULT_PROFILE, "--yes"], vault_dir)
    assert result.exit_code != 0
    assert "Cannot delete" in result.output


def test_profile_list_after_create(runner, vault_dir):
    _invoke(runner, ["create", "dev"], vault_dir)
    result = _invoke(runner, ["list"], vault_dir)
    assert "dev" in result.output
