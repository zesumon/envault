"""Visibility settings for vault keys (public / private / masked)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

VALID_MODES = {"public", "private", "masked"}


def _get_visibility_path(vault_path: Path) -> Path:
    return vault_path.parent / "visibility.json"


def _load_visibility(vault_path: Path) -> Dict[str, str]:
    p = _get_visibility_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_visibility(vault_path: Path, data: Dict[str, str]) -> None:
    p = _get_visibility_path(vault_path)
    p.write_text(json.dumps(data, indent=2, sort_keys=True))


def set_visibility(vault_path: Path, key: str, mode: str) -> None:
    if mode not in VALID_MODES:
        raise ValueError(f"Invalid mode '{mode}'. Choose from: {', '.join(sorted(VALID_MODES))}")
    data = _load_visibility(vault_path)
    data[key] = mode
    _save_visibility(vault_path, data)


def get_visibility(vault_path: Path, key: str) -> Optional[str]:
    return _load_visibility(vault_path).get(key)


def remove_visibility(vault_path: Path, key: str) -> bool:
    data = _load_visibility(vault_path)
    if key not in data:
        return False
    del data[key]
    _save_visibility(vault_path, data)
    return True


def list_visibility(vault_path: Path) -> Dict[str, str]:
    return _load_visibility(vault_path)


def display_value(value: str, mode: Optional[str]) -> str:
    if mode == "private":
        return "***"
    if mode == "masked":
        return value[:2] + "*" * max(0, len(value) - 2)
    return value
