"""CLI integration tests for the favorite commands."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envault.cli_favorites import cmd_favorite
from envault.storage import get_vault_path, save_vault, set_secret

PASSWORD = "cli-pass"


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    vault_path = get_vault_path("default")
    vault_path.parent.mkdir(parents=True, exist_ok=True)
    save_vault(vault_path, {}, PASSWORD)
    return tmp_path


def _invoke(runner: CliRunner, vault_dir: Path, args: list, password: str = PASSWORD):
    with patch("envault.cli_favorites._get_password", return_value=password):
        return runner.invoke(cmd_favorite, args, catch_exceptions=False)


def test_favorite_list_empty(runner: CliRunner, vault_dir: Path) -> None:
    result = _invoke(runner, vault_dir, ["list"])
    assert result.exit_code == 0
    assert "No favorites" in result.output


def test_favorite_add_success(runner: CliRunner, vault_dir: Path) -> None:
    vault_path = get_vault_path("default")
    set_secret(vault_path, "DB_URL", "postgres://localhost", PASSWORD)
    result = _invoke(runner, vault_dir, ["add", "DB_URL"])
    assert result.exit_code == 0
    assert "Added 'DB_URL'" in result.output


def test_favorite_add_missing_key_fails(runner: CliRunner, vault_dir: Path) -> None:
    result = _invoke(runner, vault_dir, ["add", "GHOST"])
    assert result.exit_code != 0
    assert "GHOST" in result.output


def test_favorite_list_shows_added(runner: CliRunner, vault_dir: Path) -> None:
    vault_path = get_vault_path("default")
    set_secret(vault_path, "API_KEY", "abc123", PASSWORD)
    _invoke(runner, vault_dir, ["add", "API_KEY"])
    result = _invoke(runner, vault_dir, ["list"])
    assert "API_KEY" in result.output


def test_favorite_remove_success(runner: CliRunner, vault_dir: Path) -> None:
    vault_path = get_vault_path("default")
    set_secret(vault_path, "TOKEN", "xyz", PASSWORD)
    _invoke(runner, vault_dir, ["add", "TOKEN"])
    result = _invoke(runner, vault_dir, ["remove", "TOKEN"])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_favorite_check_is_favorite(runner: CliRunner, vault_dir: Path) -> None:
    vault_path = get_vault_path("default")
    set_secret(vault_path, "SECRET", "s", PASSWORD)
    _invoke(runner, vault_dir, ["add", "SECRET"])
    result = _invoke(runner, vault_dir, ["check", "SECRET"])
    assert "is a favorite" in result.output


def test_favorite_check_not_favorite(runner: CliRunner, vault_dir: Path) -> None:
    result = _invoke(runner, vault_dir, ["check", "MISSING"])
    assert "NOT a favorite" in result.output
