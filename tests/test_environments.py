import pytest
from pathlib import Path
from envault.environments import (
    set_environment,
    get_environment,
    remove_environment,
    list_environments,
    VALID_ENVS,
)


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


def test_get_environment_returns_none_when_no_file(vault_dir):
    assert get_environment(vault_dir, "default") is None


def test_set_and_get_environment(vault_dir):
    set_environment(vault_dir, "default", "development")
    assert get_environment(vault_dir, "default") == "development"


def test_set_environment_invalid_raises(vault_dir):
    with pytest.raises(ValueError, match="Invalid environment"):
        set_environment(vault_dir, "default", "unknown")


def test_set_environment_overwrites(vault_dir):
    set_environment(vault_dir, "prod", "staging")
    set_environment(vault_dir, "prod", "production")
    assert get_environment(vault_dir, "prod") == "production"


def test_remove_environment_returns_true_when_exists(vault_dir):
    set_environment(vault_dir, "dev", "development")
    assert remove_environment(vault_dir, "dev") is True
    assert get_environment(vault_dir, "dev") is None


def test_remove_environment_returns_false_when_missing(vault_dir):
    assert remove_environment(vault_dir, "nonexistent") is False


def test_list_environments_empty(vault_dir):
    assert list_environments(vault_dir) == {}


def test_list_environments_sorted(vault_dir):
    set_environment(vault_dir, "z-profile", "test")
    set_environment(vault_dir, "a-profile", "production")
    result = list_environments(vault_dir)
    assert list(result.keys()) == ["a-profile", "z-profile"]


def test_all_valid_envs_accepted(vault_dir):
    for i, env in enumerate(VALID_ENVS):
        set_environment(vault_dir, f"profile-{i}", env)
        assert get_environment(vault_dir, f"profile-{i}") == env
