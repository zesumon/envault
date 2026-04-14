"""Tests for cli_audit commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.cli_audit import cmd_audit, cmd_audit_clear
from envault.audit import log_event, read_events


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path / "vault"


def test_audit_no_events(runner, vault_dir):
    result = runner.invoke(cmd_audit, ["--vault-dir", str(vault_dir)])
    assert result.exit_code == 0
    assert "No audit events found" in result.output


def test_audit_shows_events(runner, vault_dir):
    log_event("set", "SECRET", vault_dir=vault_dir)
    result = runner.invoke(cmd_audit, ["--vault-dir", str(vault_dir)])
    assert result.exit_code == 0
    assert "set" in result.output
    assert "SECRET" in result.output


def test_audit_tail_limits_output(runner, vault_dir):
    for i in range(5):
        log_event("set", f"KEY_{i}", vault_dir=vault_dir)
    result = runner.invoke(cmd_audit, ["--vault-dir", str(vault_dir), "--tail", "2"])
    assert result.exit_code == 0
    lines = [l for l in result.output.strip().splitlines() if l]
    assert len(lines) == 2
    assert "KEY_4" in result.output


def test_audit_filter_by_action(runner, vault_dir):
    log_event("set", "A", vault_dir=vault_dir)
    log_event("get", "B", vault_dir=vault_dir)
    result = runner.invoke(cmd_audit, ["--vault-dir", str(vault_dir), "--action", "get"])
    assert result.exit_code == 0
    assert "B" in result.output
    assert "A" not in result.output


def test_audit_clear_removes_log(runner, vault_dir):
    log_event("set", "X", vault_dir=vault_dir)
    result = runner.invoke(cmd_audit_clear, ["--vault-dir", str(vault_dir)], input="y\n")
    assert result.exit_code == 0
    assert "cleared" in result.output
    assert read_events(vault_dir=vault_dir) == []
