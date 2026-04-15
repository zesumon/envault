"""Track per-key change history in the vault."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from envault.audit import _now_iso
from envault.storage import get_vault_path


def _get_history_path(vault_path: Path) -> Path:
    return vault_path.parent / "history.json"


def _load_history(vault_path: Path) -> dict[str, list[dict[str, Any]]]:
    path = _get_history_path(vault_path)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_history(vault_path: Path, data: dict[str, list[dict[str, Any]]]) -> None:
    path = _get_history_path(vault_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def record_change(vault_path: Path, key: str, action: str, masked_value: str = "") -> None:
    """Append a change record for *key*.

    action is one of: 'set', 'delete'
    masked_value is a short preview (first 3 chars + '***') or empty for deletes.
    """
    history = _load_history(vault_path)
    entry: dict[str, Any] = {"timestamp": _now_iso(), "action": action}
    if masked_value:
        entry["preview"] = masked_value
    history.setdefault(key, []).append(entry)
    _save_history(vault_path, history)


def get_key_history(vault_path: Path, key: str) -> list[dict[str, Any]]:
    """Return the list of change records for *key*, oldest first."""
    history = _load_history(vault_path)
    return history.get(key, [])


def clear_key_history(vault_path: Path, key: str) -> int:
    """Remove all history for *key*. Returns number of records deleted."""
    history = _load_history(vault_path)
    removed = history.pop(key, [])
    _save_history(vault_path, history)
    return len(removed)


def all_keys_with_history(vault_path: Path) -> list[str]:
    """Return sorted list of keys that have at least one history entry."""
    history = _load_history(vault_path)
    return sorted(history.keys())
