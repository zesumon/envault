"""Tests for envault.profiles."""

import json
import pytest
from pathlib import Path

from envault.profiles import (
    list_profiles,
    create_profile,
    delete_profile,
    get_profile_vault_path,
    get_profiles_meta_path,
    DEFAULT_PROFILE,
)


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


def test_list_profiles_returns_default_when_no_meta(vault_dir):
    result = list_profiles(vault_dir)
    assert result == [DEFAULT_PROFILE]


def test_create_profile_adds_to_list(vault_dir):
    create_profile("staging", vault_dir)
    profiles = list_profiles(vault_dir)
    assert "staging" in profiles
    assert DEFAULT_PROFILE in profiles


def test_create_profile_invalid_name_raises(vault_dir):
    with pytest.raises(ValueError, match="Invalid profile name"):
        create_profile("my-profile", vault_dir)


def test_create_duplicate_profile_raises(vault_dir):
    create_profile("prod", vault_dir)
    with pytest.raises(ValueError, match="already exists"):
        create_profile("prod", vault_dir)


def test_delete_profile_removes_from_list(vault_dir):
    create_profile("staging", vault_dir)
    delete_profile("staging", vault_dir)
    assert "staging" not in list_profiles(vault_dir)


def test_delete_default_profile_raises(vault_dir):
    with pytest.raises(ValueError, match="Cannot delete the default profile"):
        delete_profile(DEFAULT_PROFILE, vault_dir)


def test_delete_nonexistent_profile_raises(vault_dir):
    with pytest.raises(KeyError):
        delete_profile("ghost", vault_dir)


def test_delete_profile_removes_vault_file(vault_dir):
    create_profile("temp", vault_dir)
    vault_file = vault_dir / "vault_temp.enc"
    vault_file.write_text("dummy")
    delete_profile("temp", vault_dir)
    assert not vault_file.exists()


def test_get_profile_vault_path_default(vault_dir):
    path = get_profile_vault_path(DEFAULT_PROFILE, vault_dir)
    assert path == vault_dir / "vault.enc"


def test_get_profile_vault_path_named(vault_dir):
    path = get_profile_vault_path("prod", vault_dir)
    assert path == vault_dir / "vault_prod.enc"
