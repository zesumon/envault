"""Tests for envault/tags.py"""

import os
import pytest

from envault.storage import set_secret
from envault.tags import (
    add_tag,
    remove_tag,
    get_tags,
    keys_by_tag,
    all_tags,
)

PASSWORD = "hunter2"


@pytest.fixture()
def vault_path(tmp_path):
    path = str(tmp_path / "vault.json")
    # seed a couple of secrets
    set_secret(path, PASSWORD, "DB_HOST", "localhost")
    set_secret(path, PASSWORD, "DB_PASS", "secret")
    set_secret(path, PASSWORD, "API_KEY", "abc123")
    return path


def test_get_tags_empty(vault_path):
    assert get_tags(vault_path, PASSWORD, "DB_HOST") == []


def test_add_tag_and_retrieve(vault_path):
    add_tag(vault_path, PASSWORD, "DB_HOST", "database")
    assert "database" in get_tags(vault_path, PASSWORD, "DB_HOST")


def test_add_duplicate_tag_is_idempotent(vault_path):
    add_tag(vault_path, PASSWORD, "DB_HOST", "database")
    add_tag(vault_path, PASSWORD, "DB_HOST", "database")
    assert get_tags(vault_path, PASSWORD, "DB_HOST").count("database") == 1


def test_add_tag_missing_key_raises(vault_path):
    with pytest.raises(KeyError):
        add_tag(vault_path, PASSWORD, "NONEXISTENT", "sometag")


def test_remove_tag_returns_true(vault_path):
    add_tag(vault_path, PASSWORD, "API_KEY", "external")
    result = remove_tag(vault_path, PASSWORD, "API_KEY", "external")
    assert result is True
    assert "external" not in get_tags(vault_path, PASSWORD, "API_KEY")


def test_remove_tag_not_present_returns_false(vault_path):
    result = remove_tag(vault_path, PASSWORD, "API_KEY", "ghost")
    assert result is False


def test_keys_by_tag(vault_path):
    add_tag(vault_path, PASSWORD, "DB_HOST", "database")
    add_tag(vault_path, PASSWORD, "DB_PASS", "database")
    add_tag(vault_path, PASSWORD, "API_KEY", "external")

    db_keys = keys_by_tag(vault_path, PASSWORD, "database")
    assert db_keys == ["DB_HOST", "DB_PASS"]

    ext_keys = keys_by_tag(vault_path, PASSWORD, "external")
    assert ext_keys == ["API_KEY"]


def test_keys_by_tag_no_matches(vault_path):
    assert keys_by_tag(vault_path, PASSWORD, "nope") == []


def test_all_tags(vault_path):
    add_tag(vault_path, PASSWORD, "DB_HOST", "database")
    add_tag(vault_path, PASSWORD, "DB_PASS", "database")
    add_tag(vault_path, PASSWORD, "API_KEY", "external")

    tags = all_tags(vault_path, PASSWORD)
    assert tags == ["database", "external"]


def test_all_tags_empty_vault(vault_path):
    # no tags added yet
    assert all_tags(vault_path, PASSWORD) == []
