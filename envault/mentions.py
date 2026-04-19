"""Track which keys are mentioned/referenced by other keys."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List

from envault.storage import get_vault_path


def _get_mentions_path(vault_path: Path) -> Path:
    return vault_path.parent / "mentions.json"


def _load_mentions(vault_path: Path) -> Dict[str, List[str]]:
    p = _get_mentions_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_mentions(vault_path: Path, data: Dict[str, List[str]]) -> None:
    p = _get_mentions_path(vault_path)
    p.write_text(json.dumps(data, indent=2, sort_keys=True))


def add_mention(vault_path: Path, key: str, mentioned_by: str) -> None:
    """Record that `mentioned_by` references `key`."""
    from envault.storage import load_vault
    vault = load_vault(vault_path, "")
    if key not in vault:
        raise KeyError(f"Key '{key}' not found in vault.")
    data = _load_mentions(vault_path)
    refs = data.setdefault(key, [])
    if mentioned_by not in refs:
        refs.append(mentioned_by)
        refs.sort()
    _save_mentions(vault_path, data)


def remove_mention(vault_path: Path, key: str, mentioned_by: str) -> bool:
    data = _load_mentions(vault_path)
    refs = data.get(key, [])
    if mentioned_by not in refs:
        return False
    refs.remove(mentioned_by)
    if not refs:
        del data[key]
    _save_mentions(vault_path, data)
    return True


def get_mentions(vault_path: Path, key: str) -> List[str]:
    data = _load_mentions(vault_path)
    return list(data.get(key, []))


def list_all_mentions(vault_path: Path) -> Dict[str, List[str]]:
    return _load_mentions(vault_path)


def clear_mentions(vault_path: Path, key: str) -> int:
    data = _load_mentions(vault_path)
    removed = len(data.pop(key, []))
    _save_mentions(vault_path, data)
    return removed
