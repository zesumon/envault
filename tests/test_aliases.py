"""Tests for envault.aliases."""
import pytest
from pathlib import Path

from envault.aliases import (
    add_alias,
    remove_alias,
    resolve_alias,
    list_aliases,
    update_alias,
)


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "vault" / "secrets.db"


def test_list_aliases_empty_when_no_file(vault_path):
    assert list_aliases(vault_path) == {}


def test_add_alias_and_resolve(vault_path):
    add_alias(vault_path, "db", "DATABASE_URL")
    assert resolve_alias(vault_path, "db") == "DATABASE_URL"


def test_resolve_missing_alias_returns_none(vault_path):
    assert resolve_alias(vault_path, "nope") is None


def test_add_duplicate_alias_raises(vault_path):
    add_alias(vault_path, "db", "DATABASE_URL")
    with pytest.raises(ValueError, match="already exists"):
        add_alias(vault_path, "db", "OTHER_KEY")


def test_add_invalid_alias_name_raises(vault_path):
    with pytest.raises(ValueError, match="Invalid alias"):
        add_alias(vault_path, "bad-name!", "SOME_KEY")


def test_remove_alias(vault_path):
    add_alias(vault_path, "db", "DATABASE_URL")
    remove_alias(vault_path, "db")
    assert resolve_alias(vault_path, "db") is None


def test_remove_missing_alias_raises(vault_path):
    with pytest.raises(KeyError, match="not found"):
        remove_alias(vault_path, "ghost")


def test_list_aliases_sorted(vault_path):
    add_alias(vault_path, "zz", "ZZ_KEY")
    add_alias(vault_path, "aa", "AA_KEY")
    keys = list(list_aliases(vault_path).keys())
    assert keys == ["aa", "zz"]


def test_update_alias_changes_target(vault_path):
    add_alias(vault_path, "db", "DATABASE_URL")
    update_alias(vault_path, "db", "POSTGRES_URL")
    assert resolve_alias(vault_path, "db") == "POSTGRES_URL"


def test_update_missing_alias_raises(vault_path):
    with pytest.raises(KeyError, match="not found"):
        update_alias(vault_path, "ghost", "SOME_KEY")


def test_aliases_persist_across_calls(vault_path):
    add_alias(vault_path, "s3", "AWS_S3_BUCKET")
    add_alias(vault_path, "redis", "REDIS_URL")
    result = list_aliases(vault_path)
    assert result["s3"] == "AWS_S3_BUCKET"
    assert result["redis"] == "REDIS_URL"
