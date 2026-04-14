"""Tests for envault.sync module."""

import pytest
from pathlib import Path
from unittest.mock import patch

from envault.sync import _merge, sync_vault_to_file, sync_file_to_vault


PASSWORD = "test-password"


def test_merge_primary_wins_by_default():
    primary = {"A": "1", "B": "2"}
    secondary = {"B": "old", "C": "3"}
    result = _merge(primary, secondary, conflict="vault")
    assert result["A"] == "1"
    assert result["B"] == "2"  # primary wins
    assert result["C"] == "3"


def test_merge_skip_keeps_secondary_on_conflict():
    primary = {"A": "new"}
    secondary = {"A": "old", "B": "2"}
    result = _merge(primary, secondary, conflict="skip")
    assert result["A"] == "old"  # secondary preserved
    assert result["B"] == "2"


def test_merge_adds_new_keys_from_primary():
    primary = {"NEW": "value"}
    secondary = {"EXISTING": "yes"}
    result = _merge(primary, secondary, conflict="skip")
    assert result["NEW"] == "value"
    assert result["EXISTING"] == "yes"


def test_sync_vault_to_file_creates_file(tmp_path):
    vault_secrets = {"DB": "postgres", "TOKEN": "abc"}
    env_file = tmp_path / ".env"

    with patch("envault.sync.get_vault_path") as mock_vp, \
         patch("envault.sync.load_vault", return_value=vault_secrets):
        mock_vp.return_value = tmp_path / "vault.json.enc"
        merged = sync_vault_to_file(PASSWORD, env_file)

    assert env_file.exists()
    assert merged == vault_secrets


def test_sync_vault_to_file_merges_existing(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("EXISTING=keep\nDB=old\n")
    vault_secrets = {"DB": "new", "TOKEN": "xyz"}

    with patch("envault.sync.get_vault_path") as mock_vp, \
         patch("envault.sync.load_vault", return_value=vault_secrets):
        mock_vp.return_value = tmp_path / "vault.json.enc"
        merged = sync_vault_to_file(PASSWORD, env_file, conflict="vault")

    assert merged["DB"] == "new"      # vault wins
    assert merged["EXISTING"] == "keep"
    assert merged["TOKEN"] == "xyz"


def test_sync_file_to_vault(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("API_KEY=secret\nDEBUG=true\n")
    existing_vault = {"OLD": "data"}

    saved = {}

    def fake_save(path, data, pw):
        saved.update(data)

    with patch("envault.sync.get_vault_path") as mock_vp, \
         patch("envault.sync.load_vault", return_value=existing_vault), \
         patch("envault.sync.save_vault", side_effect=fake_save):
        mock_vp.return_value = tmp_path / "vault.json.enc"
        merged = sync_file_to_vault(PASSWORD, env_file)

    assert merged["API_KEY"] == "secret"
    assert merged["DEBUG"] == "true"
    assert merged["OLD"] == "data"
