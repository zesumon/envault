"""Unit tests for envault.favorites."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.favorites import (
    add_favorite,
    clear_favorites,
    is_favorite,
    list_favorites,
    remove_favorite,
)
from envault.storage import save_vault, set_secret

PASSWORD = "test-pass"


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    path = tmp_path / ".envault" / "vault.enc"
    path.parent.mkdir(parents=True)
    save_vault(path, {}, PASSWORD)
    return path


def _add_key(vault_path: Path, key: str, value: str = "val") -> None:
    set_secret(vault_path, key, value, PASSWORD)


def test_list_favorites_empty_when_no_file(vault_path: Path) -> None:
    assert list_favorites(vault_path) == []


def test_add_favorite_and_retrieve(vault_path: Path) -> None:
    _add_key(vault_path, "DB_URL")
    add_favorite(vault_path, "DB_URL", PASSWORD)
    assert "DB_URL" in list_favorites(vault_path)


def test_add_duplicate_favorite_is_idempotent(vault_path: Path) -> None:
    _add_key(vault_path, "API_KEY")
    add_favorite(vault_path, "API_KEY", PASSWORD)
    add_favorite(vault_path, "API_KEY", PASSWORD)
    assert list_favorites(vault_path).count("API_KEY") == 1


def test_add_favorite_missing_key_raises(vault_path: Path) -> None:
    with pytest.raises(KeyError, match="GHOST"):
        add_favorite(vault_path, "GHOST", PASSWORD)


def test_remove_favorite_returns_true_when_present(vault_path: Path) -> None:
    _add_key(vault_path, "TOKEN")
    add_favorite(vault_path, "TOKEN", PASSWORD)
    assert remove_favorite(vault_path, "TOKEN") is True
    assert "TOKEN" not in list_favorites(vault_path)


def test_remove_favorite_returns_false_when_absent(vault_path: Path) -> None:
    assert remove_favorite(vault_path, "NOPE") is False


def test_is_favorite_true_and_false(vault_path: Path) -> None:
    _add_key(vault_path, "SECRET")
    add_favorite(vault_path, "SECRET", PASSWORD)
    assert is_favorite(vault_path, "SECRET") is True
    assert is_favorite(vault_path, "OTHER") is False


def test_list_favorites_is_sorted(vault_path: Path) -> None:
    for k in ["ZEBRA", "ALPHA", "MANGO"]:
        _add_key(vault_path, k)
        add_favorite(vault_path, k, PASSWORD)
    assert list_favorites(vault_path) == ["ALPHA", "MANGO", "ZEBRA"]


def test_clear_favorites_returns_count(vault_path: Path) -> None:
    for k in ["A", "B", "C"]:
        _add_key(vault_path, k)
        add_favorite(vault_path, k, PASSWORD)
    count = clear_favorites(vault_path)
    assert count == 3
    assert list_favorites(vault_path) == []
