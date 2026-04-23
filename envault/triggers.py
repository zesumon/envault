"""Triggers: associate shell commands with vault key events."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

VALID_EVENTS = ("on_set", "on_delete", "on_get", "on_expire")


def _get_triggers_path(vault_path: Path) -> Path:
    return vault_path.parent / "triggers.json"


def _load_triggers(vault_path: Path) -> Dict[str, Dict[str, List[str]]]:
    p = _get_triggers_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_triggers(vault_path: Path, data: Dict[str, Dict[str, List[str]]]) -> None:
    p = _get_triggers_path(vault_path)
    p.write_text(json.dumps(data, indent=2, sort_keys=True))


def add_trigger(vault_path: Path, key: str, event: str, command: str) -> None:
    if event not in VALID_EVENTS:
        raise ValueError(f"Invalid event '{event}'. Must be one of: {VALID_EVENTS}")
    data = _load_triggers(vault_path)
    data.setdefault(key, {})
    data[key].setdefault(event, [])
    if command not in data[key][event]:
        data[key][event].append(command)
    _save_triggers(vault_path, data)


def remove_trigger(vault_path: Path, key: str, event: str, command: str) -> bool:
    data = _load_triggers(vault_path)
    try:
        data[key][event].remove(command)
        if not data[key][event]:
            del data[key][event]
        if not data[key]:
            del data[key]
        _save_triggers(vault_path, data)
        return True
    except (KeyError, ValueError):
        return False


def get_triggers(vault_path: Path, key: str, event: Optional[str] = None) -> Dict[str, List[str]]:
    data = _load_triggers(vault_path)
    key_data = data.get(key, {})
    if event:
        return {event: key_data.get(event, [])}
    return key_data


def list_triggers(vault_path: Path) -> Dict[str, Dict[str, List[str]]]:
    return _load_triggers(vault_path)


def clear_triggers(vault_path: Path, key: str) -> None:
    data = _load_triggers(vault_path)
    if key in data:
        del data[key]
        _save_triggers(vault_path, data)
