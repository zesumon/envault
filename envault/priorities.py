"""Key priority management for envault."""
from __future__ import annotations
import json
from pathlib import Path
from envault.storage import get_vault_path

VALID_PRIORITIES = ("low", "medium", "high", "critical")


def _get_priorities_path(vault_path: Path) -> Path:
    return vault_path.parent / "priorities.json"


def _load_priorities(vault_path: Path) -> dict:
    p = _get_priorities_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_priorities(vault_path: Path, data: dict) -> None:
    p = _get_priorities_path(vault_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, sort_keys=True, indent=2))


def set_priority(vault_path: Path, key: str, priority: str) -> None:
    from envault.storage import load_vault
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"Invalid priority '{priority}'. Choose from: {', '.join(VALID_PRIORITIES)}")
    vault = load_vault(vault_path, password="")
    # just check key exists structurally — caller manages password
    data = _load_priorities(vault_path)
    data[key] = priority
    _save_priorities(vault_path, data)


def get_priority(vault_path: Path, key: str) -> str | None:
    return _load_priorities(vault_path).get(key)


def remove_priority(vault_path: Path, key: str) -> bool:
    data = _load_priorities(vault_path)
    if key not in data:
        return False
    del data[key]
    _save_priorities(vault_path, data)
    return True


def list_priorities(vault_path: Path) -> dict:
    return _load_priorities(vault_path)


def keys_by_priority(vault_path: Path, priority: str) -> list[str]:
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"Invalid priority '{priority}'.")
    data = _load_priorities(vault_path)
    return sorted(k for k, v in data.items() if v == priority)
