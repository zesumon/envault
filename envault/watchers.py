"""Watch keys for value changes and record watcher subscriptions."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envault.storage import get_vault_path


def _get_watchers_path(vault_path: Path) -> Path:
    return vault_path.parent / "watchers.json"


def _load_watchers(vault_path: Path) -> Dict[str, List[str]]:
    p = _get_watchers_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_watchers(vault_path: Path, data: Dict[str, List[str]]) -> None:
    p = _get_watchers_path(vault_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, sort_keys=True))


def add_watcher(vault_path: Path, key: str, watcher: str) -> None:
    """Subscribe *watcher* (a label/email/tag) to changes on *key*."""
    from envault.storage import load_vault

    vault = load_vault(vault_path, password="")
    # We only check key existence structurally; password validation is caller's job.
    # For watcher purposes we just verify the key exists in the raw vault file.
    raw = json.loads(vault_path.read_text()) if vault_path.exists() else {}
    if key not in raw:
        raise KeyError(f"Key {key!r} not found in vault")

    data = _load_watchers(vault_path)
    watchers = data.get(key, [])
    if watcher not in watchers:
        watchers.append(watcher)
        watchers.sort()
    data[key] = watchers
    _save_watchers(vault_path, data)


def remove_watcher(vault_path: Path, key: str, watcher: str) -> bool:
    """Unsubscribe *watcher* from *key*. Returns True if it was present."""
    data = _load_watchers(vault_path)
    watchers = data.get(key, [])
    if watcher not in watchers:
        return False
    watchers.remove(watcher)
    if watchers:
        data[key] = watchers
    else:
        data.pop(key, None)
    _save_watchers(vault_path, data)
    return True


def get_watchers(vault_path: Path, key: str) -> List[str]:
    """Return list of watchers for *key*."""
    data = _load_watchers(vault_path)
    return list(data.get(key, []))


def list_all_watchers(vault_path: Path) -> Dict[str, List[str]]:
    """Return the full watcher map."""
    return dict(_load_watchers(vault_path))


def clear_watchers(vault_path: Path, key: str) -> int:
    """Remove all watchers for *key*. Returns count removed."""
    data = _load_watchers(vault_path)
    count = len(data.pop(key, []))
    _save_watchers(vault_path, data)
    return count
