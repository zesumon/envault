import pytest
from pathlib import Path
from envault.visibility import (
    set_visibility, get_visibility, remove_visibility,
    list_visibility, display_value
)


@pytest.fixture
def vault_path(tmp_path):
    return tmp_path / "vault.enc"


def test_get_visibility_returns_none_when_no_file(vault_path):
    assert get_visibility(vault_path, "KEY") is None


def test_set_and_get_visibility(vault_path):
    set_visibility(vault_path, "API_KEY", "private")
    assert get_visibility(vault_path, "API_KEY") == "private"


def test_set_visibility_overwrites(vault_path):
    set_visibility(vault_path, "TOKEN", "public")
    set_visibility(vault_path, "TOKEN", "masked")
    assert get_visibility(vault_path, "TOKEN") == "masked"


def test_set_visibility_invalid_mode_raises(vault_path):
    with pytest.raises(ValueError, match="Invalid mode"):
        set_visibility(vault_path, "KEY", "hidden")


def test_remove_visibility_returns_true(vault_path):
    set_visibility(vault_path, "KEY", "private")
    assert remove_visibility(vault_path, "KEY") is True
    assert get_visibility(vault_path, "KEY") is None


def test_remove_visibility_missing_returns_false(vault_path):
    assert remove_visibility(vault_path, "NOPE") is False


def test_list_visibility_empty(vault_path):
    assert list_visibility(vault_path) == {}


def test_list_visibility_multiple(vault_path):
    set_visibility(vault_path, "A", "public")
    set_visibility(vault_path, "B", "masked")
    result = list_visibility(vault_path)
    assert result == {"A": "public", "B": "masked"}


def test_display_value_public():
    assert display_value("secret", "public") == "secret"
    assert display_value("secret", None) == "secret"


def test_display_value_private():
    assert display_value("secret", "private") == "***"


def test_display_value_masked():
    result = display_value("secret", "masked")
    assert result.startswith("se")
    assert "*" in result
    assert result == "se****"
