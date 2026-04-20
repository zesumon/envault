"""Tests for envault.namespaces."""

import pytest
from pathlib import Path
from envault.namespaces import (
    list_namespaces,
    create_namespace,
    delete_namespace,
    assign_key,
    unassign_key,
    get_namespace_keys,
    get_key_namespace,
)


@pytest.fixture
def vault_path(tmp_path):
    return tmp_path / "vault.db"


def test_list_namespaces_empty_when_no_file(vault_path):
    assert list_namespaces(vault_path) == []


def test_create_namespace_adds_to_list(vault_path):
    create_namespace(vault_path, "backend")
    assert "backend" in list_namespaces(vault_path)


def test_create_namespace_with_description(vault_path):
    create_namespace(vault_path, "frontend", description="UI secrets")
    assert "frontend" in list_namespaces(vault_path)


def test_list_namespaces_sorted(vault_path):
    create_namespace(vault_path, "zebra")
    create_namespace(vault_path, "alpha")
    assert list_namespaces(vault_path) == ["alpha", "zebra"]


def test_create_namespace_invalid_name_raises(vault_path):
    with pytest.raises(ValueError, match="Invalid namespace name"):
        create_namespace(vault_path, "123bad")


def test_create_duplicate_namespace_raises(vault_path):
    create_namespace(vault_path, "infra")
    with pytest.raises(ValueError, match="already exists"):
        create_namespace(vault_path, "infra")


def test_delete_namespace_removes_it(vault_path):
    create_namespace(vault_path, "temp")
    delete_namespace(vault_path, "temp")
    assert "temp" not in list_namespaces(vault_path)


def test_delete_missing_namespace_raises(vault_path):
    with pytest.raises(KeyError):
        delete_namespace(vault_path, "ghost")


def test_assign_key_and_retrieve(vault_path):
    create_namespace(vault_path, "db")
    assign_key(vault_path, "db", "DB_HOST")
    assert "DB_HOST" in get_namespace_keys(vault_path, "db")


def test_assign_key_idempotent(vault_path):
    create_namespace(vault_path, "db")
    assign_key(vault_path, "db", "DB_PORT")
    assign_key(vault_path, "db", "DB_PORT")
    assert get_namespace_keys(vault_path, "db").count("DB_PORT") == 1


def test_assign_key_missing_namespace_raises(vault_path):
    with pytest.raises(KeyError):
        assign_key(vault_path, "nope", "SOME_KEY")


def test_unassign_key(vault_path):
    create_namespace(vault_path, "api")
    assign_key(vault_path, "api", "API_KEY")
    unassign_key(vault_path, "api", "API_KEY")
    assert "API_KEY" not in get_namespace_keys(vault_path, "api")


def test_unassign_missing_key_raises(vault_path):
    create_namespace(vault_path, "api")
    with pytest.raises(KeyError):
        unassign_key(vault_path, "api", "MISSING")


def test_get_key_namespace_returns_correct(vault_path):
    create_namespace(vault_path, "infra")
    assign_key(vault_path, "infra", "REDIS_URL")
    assert get_key_namespace(vault_path, "REDIS_URL") == "infra"


def test_get_key_namespace_returns_none_when_unassigned(vault_path):
    assert get_key_namespace(vault_path, "UNASSIGNED") is None
