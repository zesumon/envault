"""TTL (time-to-live) support for secrets — expire keys after a set duration."""

import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

TTL_FILE = ".ttl.json"


def _get_ttl_path(vault_path: Path) -> Path:
    return vault_path.parent / TTL_FILE


def _load_ttl(vault_path: Path) -> dict:
    p = _get_ttl_path(vault_path)
    if not p.exists():
        return {}
    with open(p, "r") as f:
        return json.load(f)


def _save_ttl(vault_path: Path, data: dict) -> None:
    p = _get_ttl_path(vault_path)
    with open(p, "w") as f:
        json.dump(data, f, indent=2)


def set_ttl(vault_path: Path, key: str, seconds: int) -> str:
    """Set an expiry for a key. Returns the ISO expiry timestamp."""
    expires_at = (datetime.now(timezone.utc) + timedelta(seconds=seconds)).isoformat()
    data = _load_ttl(vault_path)
    data[key] = expires_at
    _save_ttl(vault_path, data)
    return expires_at


def get_ttl(vault_path: Path, key: str) -> Optional[str]:
    """Return the ISO expiry timestamp for a key, or None if not set."""
    return _load_ttl(vault_path).get(key)


def is_expired(vault_path: Path, key: str) -> bool:
    """Return True if the key has a TTL that has passed."""
    expires_at = get_ttl(vault_path, key)
    if expires_at is None:
        return False
    expiry = datetime.fromisoformat(expires_at)
    return datetime.now(timezone.utc) >= expiry


def clear_ttl(vault_path: Path, key: str) -> bool:
    """Remove TTL for a key. Returns True if it existed."""
    data = _load_ttl(vault_path)
    if key in data:
        del data[key]
        _save_ttl(vault_path, data)
        return True
    return False


def purge_expired(vault_path: Path, password: str) -> list[str]:
    """Delete all expired keys from the vault. Returns list of purged keys."""
    from envault.storage import load_vault, save_vault

    data = _load_ttl(vault_path)
    now = datetime.now(timezone.utc)
    purged = []
    for key, expires_at in list(data.items()):
        if datetime.fromisoformat(expires_at) <= now:
            purged.append(key)

    if purged:
        vault = load_vault(vault_path, password)
        for key in purged:
            vault.pop(key, None)
            del data[key]
        save_vault(vault_path, vault, password)
        _save_ttl(vault_path, data)

    return purged
