import pytest
from click.testing import CliRunner
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch

from envault.cli_expiry import cmd_expiry
from envault.storage import save_vault

PASSWORD = "testpass"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


def _invoke(runner, vault_dir, args, password=PASSWORD):
    vp = vault_dir / "default" / "secrets.db"
    vp.parent.mkdir(parents=True, exist_ok=True)
    save_vault(vp, {"K1": "v1", "K2": "v2"}, PASSWORD)
    with patch("envault.expiry.get_vault_path", return_value=vp), \
         patch("envault.cli_expiry.get_vault_path", return_value=vp), \
         patch("envault.cli_expiry._get_password", return_value=password):
        return runner.invoke(cmd_expiry, args)


def test_expiry_set_and_get(runner, vault_dir):
    r = _invoke(runner, vault_dir, ["set", "K1", "2099-01-01T00:00:00"])
    assert r.exit_code == 0
    assert "K1" in r.output


def test_expiry_get_no_expiry(runner, vault_dir):
    r = _invoke(runner, vault_dir, ["get", "K1"])
    assert r.exit_code == 0
    assert "No expiry" in r.output


def test_expiry_invalid_date(runner, vault_dir):
    r = _invoke(runner, vault_dir, ["set", "K1", "not-a-date"])
    assert r.exit_code != 0


def test_expiry_list_empty(runner, vault_dir):
    r = _invoke(runner, vault_dir, ["list"])
    assert r.exit_code == 0
    assert "No expiry" in r.output


def test_expiry_list_expired_only(runner, vault_dir):
    vp = vault_dir / "default" / "secrets.db"
    from envault.expiry import set_expiry
    past = datetime.now(timezone.utc) - timedelta(days=1)
    with patch("envault.cli_expiry.get_vault_path", return_value=vp):
        set_expiry(vp, "K1", past)
        r = runner.invoke(cmd_expiry, ["list", "--expired-only"],
                          catch_exceptions=False)
    assert "K1" in r.output


def test_expiry_remove(runner, vault_dir):
    r = _invoke(runner, vault_dir, ["remove", "K1"])
    assert r.exit_code == 0
    assert "No expiry" in r.output
