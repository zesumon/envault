"""Pin secrets to prevent accidental modification or deletion."""

import json
from pathlib import Path
from envault.storage import get_vault_path


def _get_pins_path(vault_path: Path) -> Path:
    return vault_path.parent / "pins.json"


def _load_pins(vault_path: Path) -> list:
    p = _get_pins_path(vault_path)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save_pins(vault_path: Path, pins: list) -> None:
    p = _get_pins_path(vault_path)
    p.write_text(json.dumps(sorted(set(pins)), indent=2))


def pin_key(vault_path: Path, key: str) -> None:
    """Pin a key. Raises KeyError if key not in vault."""
    from envault.storage import load_vault
    vault = load_vault(vault_path)
    if key not in vault:
        raise KeyError(f"Key '{key}' not found in vault")
    pins = _load_pins(vault_path)
    if key not in pins:
        pins.append(key)
    _save_pins(vault_path, pins)


def unpin_key(vault_path: Path, key: str) -> None:
    """Unpin a key. Raises KeyError if not pinned."""
    pins = _load_pins(vault_path)
    if key not in pins:
        raise KeyError(f"Key '{key}' is not pinned")
    pins.remove(key)
    _save_pins(vault_path, pins)


def is_pinned(vault_path: Path, key: str) -> bool:
    return key in _load_pins(vault_path)


def list_pins(vault_path: Path) -> list:
    return _load_pins(vault_path)


def assert_not_pinned(vault_path: Path, key: str) -> None:
    """Raise PermissionError if key is pinned."""
    if is_pinned(vault_path, key):
        raise PermissionError(f"Key '{key}' is pinned and cannot be modified or deleted")
