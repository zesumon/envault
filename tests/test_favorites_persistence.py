"""Persistence tests — verify favorites.json on disk stays consistent."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.favorites import (
    _get_favorites_path,
    add_favorite,
    clear_favorites,
    list_favorites,
    remove_favorite,
)
from envault.storage import save_vault, set_secret

PASSWORD = "persist-pass"


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    vault_path = tmp_path / ".envault" / "vault.enc"
    vault_path.parent.mkdir(parents=True)
    save_vault(vault_path, {}, PASSWORD)
    return tmp_path


def _vault(vault_dir: Path) -> Path:
    return vault_dir / ".envault" / "vault.enc"


def test_favorites_file_is_valid_json(vault_dir: Path) -> None:
    vp = _vault(vault_dir)
    set_secret(vp, "KEY", "val", PASSWORD)
    add_favorite(vp, "KEY", PASSWORD)
    raw = _get_favorites_path(vp).read_text()
    data = json.loads(raw)
    assert isinstance(data, list)


def test_multiple_favorites_persist(vault_dir: Path) -> None:
    vp = _vault(vault_dir)
    for k in ["A", "B", "C"]:
        set_secret(vp, k, "v", PASSWORD)
        add_favorite(vp, k, PASSWORD)
    assert set(list_favorites(vp)) == {"A", "B", "C"}


def test_remove_leaves_others_intact(vault_dir: Path) -> None:
    vp = _vault(vault_dir)
    for k in ["X", "Y", "Z"]:
        set_secret(vp, k, "v", PASSWORD)
        add_favorite(vp, k, PASSWORD)
    remove_favorite(vp, "Y")
    remaining = list_favorites(vp)
    assert "Y" not in remaining
    assert "X" in remaining
    assert "Z" in remaining


def test_clear_results_in_empty_list(vault_dir: Path) -> None:
    vp = _vault(vault_dir)
    for k in ["P", "Q"]:
        set_secret(vp, k, "v", PASSWORD)
        add_favorite(vp, k, PASSWORD)
    clear_favorites(vp)
    assert list_favorites(vp) == []
    raw = _get_favorites_path(vp).read_text()
    assert json.loads(raw) == []
