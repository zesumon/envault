"""Persistence tests — verify remotes.json is written correctly."""

import json
import pytest
from pathlib import Path

from envault.remotes import add_remote, remove_remote, update_remote, _get_remotes_path


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


def test_remotes_file_is_valid_json(vault_dir):
    add_remote(vault_dir, "origin", "https://example.com")
    path = _get_remotes_path(vault_dir)
    assert path.exists()
    data = json.loads(path.read_text())
    assert isinstance(data, dict)
    assert data["origin"] == "https://example.com"


def test_multiple_remotes_persist(vault_dir):
    add_remote(vault_dir, "origin", "https://a.example.com")
    add_remote(vault_dir, "backup", "https://b.example.com")
    data = json.loads(_get_remotes_path(vault_dir).read_text())
    assert len(data) == 2
    assert "origin" in data
    assert "backup" in data


def test_update_persists_new_url(vault_dir):
    add_remote(vault_dir, "origin", "https://old.example.com")
    update_remote(vault_dir, "origin", "https://new.example.com")
    data = json.loads(_get_remotes_path(vault_dir).read_text())
    assert data["origin"] == "https://new.example.com"


def test_remove_leaves_others_intact(vault_dir):
    add_remote(vault_dir, "origin", "https://a.example.com")
    add_remote(vault_dir, "backup", "https://b.example.com")
    remove_remote(vault_dir, "origin")
    data = json.loads(_get_remotes_path(vault_dir).read_text())
    assert "origin" not in data
    assert "backup" in data


def test_url_is_stripped_on_save(vault_dir):
    add_remote(vault_dir, "origin", "  https://example.com  ")
    data = json.loads(_get_remotes_path(vault_dir).read_text())
    assert data["origin"] == "https://example.com"
