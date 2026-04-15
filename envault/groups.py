"""Group management for envault — organize secrets into named groups."""

import json
from pathlib import Path
from typing import Dict, List, Optional

from envault.storage import get_vault_path, load_vault


def _get_groups_path(vault_path: Path) -> Path:
    return vault_path.parent / "groups.json"


def _load_groups(vault_path: Path) -> Dict[str, List[str]]:
    path = _get_groups_path(vault_path)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_groups(vault_path: Path, groups: Dict[str, List[str]]) -> None:
    path = _get_groups_path(vault_path)
    with open(path, "w") as f:
        json.dump(groups, f, indent=2, sort_keys=True)


def list_groups(vault_path: Path) -> List[str]:
    """Return sorted list of group names."""
    return sorted(_load_groups(vault_path).keys())


def create_group(vault_path: Path, group: str) -> None:
    """Create a new empty group. Raises ValueError if it already exists."""
    if not group.isidentifier():
        raise ValueError(f"Invalid group name: {group!r}")
    groups = _load_groups(vault_path)
    if group in groups:
        raise ValueError(f"Group {group!r} already exists")
    groups[group] = []
    _save_groups(vault_path, groups)


def delete_group(vault_path: Path, group: str) -> None:
    """Delete a group. Raises KeyError if not found."""
    groups = _load_groups(vault_path)
    if group not in groups:
        raise KeyError(f"Group {group!r} not found")
    del groups[group]
    _save_groups(vault_path, groups)


def add_key_to_group(vault_path: Path, group: str, key: str) -> None:
    """Add a secret key to a group. Key must exist in vault."""
    vault = load_vault(vault_path)
    if key not in vault.get("secrets", {}):
        raise KeyError(f"Key {key!r} not found in vault")
    groups = _load_groups(vault_path)
    if group not in groups:
        raise KeyError(f"Group {group!r} not found")
    if key not in groups[group]:
        groups[group].append(key)
        groups[group].sort()
    _save_groups(vault_path, groups)


def remove_key_from_group(vault_path: Path, group: str, key: str) -> None:
    """Remove a secret key from a group."""
    groups = _load_groups(vault_path)
    if group not in groups:
        raise KeyError(f"Group {group!r} not found")
    if key not in groups[group]:
        raise KeyError(f"Key {key!r} not in group {group!r}")
    groups[group].remove(key)
    _save_groups(vault_path, groups)


def get_group_keys(vault_path: Path, group: str) -> List[str]:
    """Return sorted list of keys in a group."""
    groups = _load_groups(vault_path)
    if group not in groups:
        raise KeyError(f"Group {group!r} not found")
    return sorted(groups[group])


def find_groups_for_key(vault_path: Path, key: str) -> List[str]:
    """Return all groups that contain a given key."""
    groups = _load_groups(vault_path)
    return sorted(g for g, keys in groups.items() if key in keys)
