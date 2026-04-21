"""Key lifecycle state management for envault."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envault.storage import get_vault_path

VALID_STATES = ("active", "deprecated", "archived", "draft")


def _get_lifecycle_path(vault_path: Path) -> Path:
    return vault_path.parent / "lifecycle.json"


def _load_lifecycle(vault_path: Path) -> dict:
    p = _get_lifecycle_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_lifecycle(vault_path: Path, data: dict) -> None:
    p = _get_lifecycle_path(vault_path)
    p.write_text(json.dumps(data, indent=2, sort_keys=True))


def set_lifecycle(vault_path: Path, key: str, state: str) -> None:
    """Set the lifecycle state for a key."""
    if state not in VALID_STATES:
        raise ValueError(f"Invalid state '{state}'. Choose from: {', '.join(VALID_STATES)}")
    data = _load_lifecycle(vault_path)
    data[key] = state
    _save_lifecycle(vault_path, data)


def get_lifecycle(vault_path: Path, key: str) -> Optional[str]:
    """Return the lifecycle state of a key, or None if not set."""
    data = _load_lifecycle(vault_path)
    return data.get(key)


def remove_lifecycle(vault_path: Path, key: str) -> bool:
    """Remove lifecycle state for a key. Returns True if it existed."""
    data = _load_lifecycle(vault_path)
    if key not in data:
        return False
    del data[key]
    _save_lifecycle(vault_path, data)
    return True


def list_lifecycle(vault_path: Path) -> dict[str, str]:
    """Return all key->state mappings, sorted by key."""
    data = _load_lifecycle(vault_path)
    return dict(sorted(data.items()))


def keys_by_state(vault_path: Path, state: str) -> list[str]:
    """Return all keys with a given lifecycle state."""
    if state not in VALID_STATES:
        raise ValueError(f"Invalid state '{state}'. Choose from: {', '.join(VALID_STATES)}")
    data = _load_lifecycle(vault_path)
    return sorted(k for k, v in data.items() if v == state)
