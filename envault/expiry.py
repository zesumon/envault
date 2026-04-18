"""Key expiry: set an expiration date on secrets and list/purge expired ones."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from envault.storage import get_vault_path, load_vault


def _get_expiry_path(vault_path: Path) -> Path:
    return vault_path.parent / "expiry.json"


def _load_expiry(vault_path: Path) -> dict:
    p = _get_expiry_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_expiry(vault_path: Path, data: dict) -> None:
    _get_expiry_path(vault_path).write_text(json.dumps(data, indent=2))


def set_expiry(vault_path: Path, key: str, expires_at: datetime) -> str:
    vault = load_vault(vault_path, password=None)  # existence check via storage
    expiry = _load_expiry(vault_path)
    iso = expires_at.astimezone(timezone.utc).isoformat()
    expiry[key] = iso
    _save_expiry(vault_path, expiry)
    return iso


def get_expiry(vault_path: Path, key: str) -> Optional[str]:
    return _load_expiry(vault_path).get(key)


def remove_expiry(vault_path: Path, key: str) -> bool:
    expiry = _load_expiry(vault_path)
    if key not in expiry:
        return False
    del expiry[key]
    _save_expiry(vault_path, expiry)
    return True


def list_expired(vault_path: Path) -> list[str]:
    now = datetime.now(timezone.utc)
    expiry = _load_expiry(vault_path)
    return sorted(k for k, v in expiry.items() if datetime.fromisoformat(v) <= now)


def list_expiry(vault_path: Path) -> list[tuple[str, str]]:
    expiry = _load_expiry(vault_path)
    return sorted(expiry.items())


def purge_expired(vault_path: Path, password: str) -> list[str]:
    from envault.storage import load_vault, save_vault
    expired = list_expired(vault_path)
    if not expired:
        return []
    vault = load_vault(vault_path, password)
    expiry = _load_expiry(vault_path)
    for key in expired:
        vault.pop(key, None)
        expiry.pop(key, None)
    save_vault(vault_path, vault, password)
    _save_expiry(vault_path, expiry)
    return expired
