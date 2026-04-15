"""Tests for envault/templates.py"""

import pytest
from pathlib import Path
from envault.templates import (
    list_templates,
    save_template,
    delete_template,
    get_template_keys,
    check_missing_keys,
)


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path / ".envault"


def test_list_templates_empty(vault_dir):
    assert list_templates(vault_dir) == []


def test_save_and_list_template(vault_dir):
    save_template(vault_dir, "django", ["SECRET_KEY", "DATABASE_URL"])
    assert "django" in list_templates(vault_dir)


def test_save_template_sorts_keys(vault_dir):
    save_template(vault_dir, "app", ["Z_KEY", "A_KEY", "M_KEY"])
    keys = get_template_keys(vault_dir, "app")
    assert keys == ["A_KEY", "M_KEY", "Z_KEY"]


def test_save_template_deduplicates_keys(vault_dir):
    save_template(vault_dir, "app", ["KEY", "KEY", "OTHER"])
    keys = get_template_keys(vault_dir, "app")
    assert keys.count("KEY") == 1


def test_save_template_invalid_name_raises(vault_dir):
    with pytest.raises(ValueError, match="Invalid template name"):
        save_template(vault_dir, "bad name!", ["KEY"])


def test_save_template_empty_keys_raises(vault_dir):
    with pytest.raises(ValueError, match="at least one key"):
        save_template(vault_dir, "empty", [])


def test_get_template_keys_missing_raises(vault_dir):
    with pytest.raises(KeyError, match="not found"):
        get_template_keys(vault_dir, "nonexistent")


def test_delete_template(vault_dir):
    save_template(vault_dir, "tpl", ["A"])
    delete_template(vault_dir, "tpl")
    assert "tpl" not in list_templates(vault_dir)


def test_delete_missing_template_raises(vault_dir):
    with pytest.raises(KeyError):
        delete_template(vault_dir, "ghost")


def test_check_missing_keys_all_present(vault_dir):
    save_template(vault_dir, "t", ["A", "B"])
    missing = check_missing_keys(vault_dir, "t", ["A", "B", "C"])
    assert missing == []


def test_check_missing_keys_some_absent(vault_dir):
    save_template(vault_dir, "t", ["A", "B", "C"])
    missing = check_missing_keys(vault_dir, "t", ["A"])
    assert set(missing) == {"B", "C"}


def test_save_template_overwrites_existing(vault_dir):
    save_template(vault_dir, "t", ["OLD"])
    save_template(vault_dir, "t", ["NEW"])
    keys = get_template_keys(vault_dir, "t")
    assert keys == ["NEW"]
