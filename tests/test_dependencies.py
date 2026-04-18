import pytest
from pathlib import Path
from envault.dependencies import (
    add_dependency, remove_dependency, get_dependencies,
    get_dependents, list_all_dependencies, clear_dependencies,
)


@pytest.fixture
def vault_path(tmp_path):
    vp = tmp_path / ".envault" / "vault.enc"
    vp.parent.mkdir(parents=True)
    vp.touch()
    return vp


def test_get_dependencies_empty_when_no_file(vault_path):
    assert get_dependencies(vault_path, "DB_URL") == []


def test_add_dependency_and_retrieve(vault_path):
    add_dependency(vault_path, "DB_URL", "DB_HOST")
    assert "DB_HOST" in get_dependencies(vault_path, "DB_URL")


def test_add_multiple_dependencies(vault_path):
    add_dependency(vault_path, "APP_DSN", "DB_HOST")
    add_dependency(vault_path, "APP_DSN", "DB_PORT")
    deps = get_dependencies(vault_path, "APP_DSN")
    assert "DB_HOST" in deps
    assert "DB_PORT" in deps
    assert deps == sorted(deps)


def test_add_duplicate_dependency_is_idempotent(vault_path):
    add_dependency(vault_path, "KEY_A", "KEY_B")
    add_dependency(vault_path, "KEY_A", "KEY_B")
    assert get_dependencies(vault_path, "KEY_A").count("KEY_B") == 1


def test_remove_dependency_returns_true(vault_path):
    add_dependency(vault_path, "KEY_A", "KEY_B")
    result = remove_dependency(vault_path, "KEY_A", "KEY_B")
    assert result is True
    assert get_dependencies(vault_path, "KEY_A") == []


def test_remove_missing_dependency_returns_false(vault_path):
    result = remove_dependency(vault_path, "KEY_A", "KEY_B")
    assert result is False


def test_get_dependents(vault_path):
    add_dependency(vault_path, "DB_URL", "DB_HOST")
    add_dependency(vault_path, "APP_DSN", "DB_HOST")
    dependents = get_dependents(vault_path, "DB_HOST")
    assert "DB_URL" in dependents
    assert "APP_DSN" in dependents


def test_get_dependents_empty(vault_path):
    assert get_dependents(vault_path, "ORPHAN") == []


def test_list_all_dependencies(vault_path):
    add_dependency(vault_path, "A", "B")
    add_dependency(vault_path, "C", "D")
    all_deps = list_all_dependencies(vault_path)
    assert "A" in all_deps
    assert "C" in all_deps


def test_clear_dependencies_removes_key(vault_path):
    add_dependency(vault_path, "KEY_A", "KEY_B")
    clear_dependencies(vault_path, "KEY_A")
    assert get_dependencies(vault_path, "KEY_A") == []
