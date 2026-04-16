"""Access control: restrict which keys a profile/user can read or write."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Optional


def _get_access_path(vault_path: Path) -> Path:
    return vault_path.parent / "access.json"


def _load_access(vault_path: Path) -> Dict[str, Dict[str, List[str]]]:
    p = _get_access_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_access(vault_path: Path, data: Dict[str, Dict[str, List[str]]]) -> None:
    p = _get_access_path(vault_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, sort_keys=True))


def set_access(vault_path: Path, profile: str, key: str, modes: List[str]) -> None:
    """Grant a profile read/write access to a key. modes: list of 'read','write'."""
    valid = {"read", "write"}
    bad = set(modes) - valid
    if bad:
        raise ValueError(f"Invalid modes: {bad}. Must be 'read' and/or 'write'.")
    data = _load_access(vault_path)
    data.setdefault(profile, {})[key] = sorted(set(modes))
    _save_access(vault_path, data)


def remove_access(vault_path: Path, profile: str, key: str) -> None:
    data = _load_access(vault_path)
    if profile in data and key in data[profile]:
        del data[profile][key]
        if not data[profile]:
            del data[profile]
        _save_access(vault_path, data)


def get_access(vault_path: Path, profile: str, key: str) -> Optional[List[str]]:
    data = _load_access(vault_path)
    return data.get(profile, {}).get(key)


def can_read(vault_path: Path, profile: str, key: str) -> bool:
    modes = get_access(vault_path, profile, key)
    if modes is None:
        return True  # no restriction means open
    return "read" in modes


def can_write(vault_path: Path, profile: str, key: str) -> bool:
    modes = get_access(vault_path, profile, key)
    if modes is None:
        return True
    return "write" in modes


def list_access(vault_path: Path, profile: str) -> Dict[str, List[str]]:
    data = _load_access(vault_path)
    return dict(data.get(profile, {}))
