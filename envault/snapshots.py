"""Snapshot support: save and restore point-in-time copies of the vault."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from envault.storage import load_vault, save_vault, get_vault_path


def _get_snapshots_dir(vault_dir: Optional[str] = None) -> Path:
    base = Path(get_vault_path(vault_dir)).parent
    return base / "snapshots"


def _now_slug() -> str:
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")


def list_snapshots(vault_dir: Optional[str] = None) -> List[str]:
    """Return snapshot names sorted newest-first."""
    snap_dir = _get_snapshots_dir(vault_dir)
    if not snap_dir.exists():
        return []
    names = [p.stem for p in snap_dir.glob("*.json")]
    return sorted(names, reverse=True)


def create_snapshot(
    password: str,
    name: Optional[str] = None,
    vault_dir: Optional[str] = None,
) -> str:
    """Snapshot current vault contents. Returns the snapshot name."""
    snap_dir = _get_snapshots_dir(vault_dir)
    snap_dir.mkdir(parents=True, exist_ok=True)

    vault = load_vault(password, vault_dir=vault_dir)
    snap_name = name or _now_slug()
    snap_path = snap_dir / f"{snap_name}.json"
    if snap_path.exists():
        raise ValueError(f"Snapshot '{snap_name}' already exists.")

    snap_path.write_text(json.dumps(vault, indent=2), encoding="utf-8")
    return snap_name


def restore_snapshot(
    name: str,
    password: str,
    vault_dir: Optional[str] = None,
) -> int:
    """Restore vault from a snapshot. Returns number of keys restored."""
    snap_dir = _get_snapshots_dir(vault_dir)
    snap_path = snap_dir / f"{name}.json"
    if not snap_path.exists():
        raise FileNotFoundError(f"Snapshot '{name}' not found.")

    data = json.loads(snap_path.read_text(encoding="utf-8"))
    save_vault(data, password, vault_dir=vault_dir)
    return len(data)


def delete_snapshot(name: str, vault_dir: Optional[str] = None) -> None:
    """Delete a named snapshot."""
    snap_dir = _get_snapshots_dir(vault_dir)
    snap_path = snap_dir / f"{name}.json"
    if not snap_path.exists():
        raise FileNotFoundError(f"Snapshot '{name}' not found.")
    snap_path.unlink()
