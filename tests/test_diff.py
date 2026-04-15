"""Tests for envault.diff module."""

import os
import pytest

from envault.diff import diff_vault_vs_file, format_diff, DiffEntry
from envault.storage import save_vault


@pytest.fixture()
def vault_path(tmp_path):
    return str(tmp_path / "vault.json")


PASSWORD = "test-pass"


def _make_vault(path, secrets):
    save_vault(path, PASSWORD, {"secrets": secrets})


def _make_dotenv(tmp_path, content):
    p = tmp_path / ".env"
    p.write_text(content)
    return str(p)


def test_diff_no_differences(tmp_path, vault_path):
    _make_vault(vault_path, {"KEY": "val"})
    dotenv = _make_dotenv(tmp_path, "KEY=val\n")
    entries = diff_vault_vs_file(vault_path, dotenv, PASSWORD)
    assert entries == []


def test_diff_show_unchanged(tmp_path, vault_path):
    _make_vault(vault_path, {"KEY": "val"})
    dotenv = _make_dotenv(tmp_path, "KEY=val\n")
    entries = diff_vault_vs_file(vault_path, dotenv, PASSWORD, show_unchanged=True)
    assert len(entries) == 1
    assert entries[0].status == "unchanged"


def test_diff_added_key(tmp_path, vault_path):
    _make_vault(vault_path, {})
    dotenv = _make_dotenv(tmp_path, "NEW_KEY=hello\n")
    entries = diff_vault_vs_file(vault_path, dotenv, PASSWORD)
    assert len(entries) == 1
    assert entries[0].status == "added"
    assert entries[0].key == "NEW_KEY"
    assert entries[0].file_value == "hello"


def test_diff_removed_key(tmp_path, vault_path):
    _make_vault(vault_path, {"OLD_KEY": "bye"})
    dotenv = _make_dotenv(tmp_path, "")
    entries = diff_vault_vs_file(vault_path, dotenv, PASSWORD)
    assert len(entries) == 1
    assert entries[0].status == "removed"
    assert entries[0].vault_value == "bye"


def test_diff_changed_key(tmp_path, vault_path):
    _make_vault(vault_path, {"K": "old"})
    dotenv = _make_dotenv(tmp_path, "K=new\n")
    entries = diff_vault_vs_file(vault_path, dotenv, PASSWORD)
    assert len(entries) == 1
    assert entries[0].status == "changed"
    assert entries[0].vault_value == "old"
    assert entries[0].file_value == "new"


def test_diff_missing_dotenv(tmp_path, vault_path):
    _make_vault(vault_path, {"A": "1"})
    entries = diff_vault_vs_file(vault_path, str(tmp_path / "nonexistent.env"), PASSWORD)
    assert len(entries) == 1
    assert entries[0].status == "removed"


def test_format_diff_no_entries():
    assert format_diff([]) == "No differences found."


def test_format_diff_hides_values():
    entries = [DiffEntry(key="SECRET", status="added", file_value="s3cr3t")]
    output = format_diff(entries, hide_values=True)
    assert "s3cr3t" not in output
    assert "SECRET" in output


def test_format_diff_shows_changed_values():
    entries = [DiffEntry(key="K", status="changed", vault_value="old", file_value="new")]
    output = format_diff(entries)
    assert "old" in output
    assert "new" in output
