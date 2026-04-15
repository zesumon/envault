"""Integration tests: templates survive save/reload cycles."""

import json
import pytest
from pathlib import Path
from envault.templates import save_template, list_templates, get_template_keys, delete_template


@pytest.fixture
def vault_dir(tmp_path):
    d = tmp_path / ".envault"
    d.mkdir()
    return d


def test_templates_file_is_valid_json(vault_dir):
    save_template(vault_dir, "svc", ["PORT", "HOST"])
    tfile = vault_dir / "templates.json"
    assert tfile.exists()
    data = json.loads(tfile.read_text())
    assert "svc" in data


def test_multiple_templates_persist(vault_dir):
    save_template(vault_dir, "alpha", ["A"])
    save_template(vault_dir, "beta", ["B", "C"])
    names = list_templates(vault_dir)
    assert names == ["alpha", "beta"]


def test_overwrite_does_not_duplicate(vault_dir):
    save_template(vault_dir, "t", ["X"])
    save_template(vault_dir, "t", ["Y", "Z"])
    names = list_templates(vault_dir)
    assert names.count("t") == 1
    assert get_template_keys(vault_dir, "t") == ["Y", "Z"]


def test_delete_leaves_others_intact(vault_dir):
    save_template(vault_dir, "keep", ["K"])
    save_template(vault_dir, "remove", ["R"])
    delete_template(vault_dir, "remove")
    assert list_templates(vault_dir) == ["keep"]


def test_templates_dir_created_if_missing(tmp_path):
    nested = tmp_path / "deep" / "vault"
    # directory does not exist yet
    save_template(nested, "new", ["KEY"])
    assert (nested / "templates.json").exists()
