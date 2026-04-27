"""Ownership tracking for vault keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envault.storage import get_vault_path


def _get_ownership_path(vault_path: Path) -> Path:
    return vault_path.parent / "ownership.json"


def _load_ownership(vault_path: Path) -> dict:
    p = _get_ownership_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_ownership(vault_path: Path, data: dict) -> None:
    p = _get_ownership_path(vault_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, sort_keys=True))


def set_owner(vault_path: Path, key: str, owner: str) -> None:
    """Assign an owner to a key."""
    if not owner or not owner.strip():
        raise ValueError("Owner must be a non-empty string.")
    data = _load_ownership(vault_path)
    data[key] = owner.strip()
    _save_ownership(vault_path, data)


def get_owner(vault_path: Path, key: str) -> Optional[str]:
    """Return the owner of a key, or None if unset."""
    data = _load_ownership(vault_path)
    return data.get(key)


def remove_owner(vault_path: Path, key: str) -> bool:
    """Remove ownership record for a key. Returns True if removed."""
    data = _load_ownership(vault_path)
    if key in data:
        del data[key]
        _save_ownership(vault_path, data)
        return True
    return False


def list_owned_keys(vault_path: Path, owner: str) -> list[str]:
    """Return all keys owned by the given owner, sorted."""
    data = _load_ownership(vault_path)
    return sorted(k for k, v in data.items() if v == owner)


def list_all_ownership(vault_path: Path) -> dict[str, str]:
    """Return a copy of the full ownership mapping."""
    return dict(_load_ownership(vault_path))
