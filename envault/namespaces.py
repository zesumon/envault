"""Namespace support for grouping secrets under logical prefixes."""

import json
import re
from pathlib import Path
from typing import List, Optional

_VALID_NAME = re.compile(r'^[a-zA-Z][a-zA-Z0-9_-]*$')


def _get_namespaces_path(vault_path: Path) -> Path:
    return vault_path.parent / "namespaces.json"


def _load_namespaces(vault_path: Path) -> dict:
    p = _get_namespaces_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_namespaces(vault_path: Path, data: dict) -> None:
    p = _get_namespaces_path(vault_path)
    p.write_text(json.dumps(data, indent=2, sort_keys=True))


def list_namespaces(vault_path: Path) -> List[str]:
    """Return sorted list of defined namespace names."""
    data = _load_namespaces(vault_path)
    return sorted(data.keys())


def create_namespace(vault_path: Path, name: str, description: str = "") -> None:
    """Create a new namespace. Raises ValueError on invalid or duplicate name."""
    if not _VALID_NAME.match(name):
        raise ValueError(f"Invalid namespace name: {name!r}")
    data = _load_namespaces(vault_path)
    if name in data:
        raise ValueError(f"Namespace already exists: {name!r}")
    data[name] = {"description": description, "keys": []}
    _save_namespaces(vault_path, data)


def delete_namespace(vault_path: Path, name: str) -> None:
    """Delete a namespace. Raises KeyError if not found."""
    data = _load_namespaces(vault_path)
    if name not in data:
        raise KeyError(f"Namespace not found: {name!r}")
    del data[name]
    _save_namespaces(vault_path, data)


def assign_key(vault_path: Path, namespace: str, key: str) -> None:
    """Assign a key to a namespace. Idempotent."""
    data = _load_namespaces(vault_path)
    if namespace not in data:
        raise KeyError(f"Namespace not found: {namespace!r}")
    if key not in data[namespace]["keys"]:
        data[namespace]["keys"].append(key)
        data[namespace]["keys"].sort()
    _save_namespaces(vault_path, data)


def unassign_key(vault_path: Path, namespace: str, key: str) -> None:
    """Remove a key from a namespace. Raises KeyError if not assigned."""
    data = _load_namespaces(vault_path)
    if namespace not in data:
        raise KeyError(f"Namespace not found: {namespace!r}")
    if key not in data[namespace]["keys"]:
        raise KeyError(f"Key {key!r} not in namespace {namespace!r}")
    data[namespace]["keys"].remove(key)
    _save_namespaces(vault_path, data)


def get_namespace_keys(vault_path: Path, namespace: str) -> List[str]:
    """Return sorted keys assigned to a namespace."""
    data = _load_namespaces(vault_path)
    if namespace not in data:
        raise KeyError(f"Namespace not found: {namespace!r}")
    return list(data[namespace]["keys"])


def get_key_namespace(vault_path: Path, key: str) -> Optional[str]:
    """Return the namespace a key belongs to, or None."""
    data = _load_namespaces(vault_path)
    for name, info in data.items():
        if key in info["keys"]:
            return name
    return None
