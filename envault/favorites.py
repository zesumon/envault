"""Favorites — mark frequently used keys for quick access."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from envault.storage import get_vault_path, load_vault


def _get_favorites_path(vault_path: Path) -> Path:
    return vault_path.parent / "favorites.json"


def _load_favorites(vault_path: Path) -> List[str]:
    p = _get_favorites_path(vault_path)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save_favorites(vault_path: Path, favorites: List[str]) -> None:
    p = _get_favorites_path(vault_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(sorted(set(favorites)), indent=2))


def add_favorite(vault_path: Path, key: str, password: str) -> None:
    """Mark *key* as a favorite. Raises KeyError if key does not exist in vault."""
    vault = load_vault(vault_path, password)
    if key not in vault:
        raise KeyError(f"Key '{key}' not found in vault")
    favs = _load_favorites(vault_path)
    if key not in favs:
        favs.append(key)
    _save_favorites(vault_path, favs)


def remove_favorite(vault_path: Path, key: str) -> bool:
    """Remove *key* from favorites. Returns True if it was present."""
    favs = _load_favorites(vault_path)
    if key not in favs:
        return False
    favs.remove(key)
    _save_favorites(vault_path, favs)
    return True


def list_favorites(vault_path: Path) -> List[str]:
    """Return sorted list of favorite keys."""
    return _load_favorites(vault_path)


def is_favorite(vault_path: Path, key: str) -> bool:
    return key in _load_favorites(vault_path)


def clear_favorites(vault_path: Path) -> int:
    """Remove all favorites. Returns the count cleared."""
    favs = _load_favorites(vault_path)
    count = len(favs)
    _save_favorites(vault_path, [])
    return count
