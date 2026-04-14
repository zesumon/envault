"""Audit log for tracking vault operations."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

AUDIT_FILENAME = "audit.log"


def get_audit_path(vault_dir: Optional[Path] = None) -> Path:
    """Return the path to the audit log file."""
    if vault_dir is None:
        vault_dir = Path.home() / ".envault"
    return vault_dir / AUDIT_FILENAME


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_event(action: str, key: str, vault_dir: Optional[Path] = None) -> None:
    """Append a single audit event to the log."""
    audit_path = get_audit_path(vault_dir)
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": _now_iso(),
        "action": action,
        "key": key,
    }
    with audit_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def read_events(vault_dir: Optional[Path] = None) -> list[dict]:
    """Return all audit events as a list of dicts."""
    audit_path = get_audit_path(vault_dir)
    if not audit_path.exists():
        return []
    events = []
    with audit_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return events


def clear_audit_log(vault_dir: Optional[Path] = None) -> None:
    """Delete the audit log file if it exists."""
    audit_path = get_audit_path(vault_dir)
    if audit_path.exists():
        audit_path.unlink()
