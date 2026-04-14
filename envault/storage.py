"""Local encrypted storage for envault secrets."""

import json
import os
from pathlib import Path
from typing import Optional

from envault.crypto import encrypt, decrypt

DEFAULT_VAULT_DIR = Path.home() / ".envault"
VAULT_FILE_NAME = "vault.enc"


def get_vault_path(vault_dir: Optional[Path] = None) -> Path:
    """Return the path to the vault file."""
    base = vault_dir or DEFAULT_VAULT_DIR
    return base / VAULT_FILE_NAME


def _ensure_vault_dir(vault_path: Path) -> None:
    vault_path.parent.mkdir(parents=True, exist_ok=True)


def load_vault(password: str, vault_path: Optional[Path] = None) -> dict:
    """Load and decrypt the vault, returning a dict of env entries.

    Returns an empty dict if the vault file does not exist yet.
    """
    path = vault_path or get_vault_path()
    if not path.exists():
        return {}
    blob = path.read_text(encoding="utf-8").strip()
    raw = decrypt(blob, password)
    return json.loads(raw)


def save_vault(data: dict, password: str, vault_path: Optional[Path] = None) -> None:
    """Encrypt and persist the vault dict to disk."""
    path = vault_path or get_vault_path()
    _ensure_vault_dir(path)
    raw = json.dumps(data)
    blob = encrypt(raw, password)
    path.write_text(blob, encoding="utf-8")


def set_secret(key: str, value: str, password: str, vault_path: Optional[Path] = None) -> None:
    """Insert or update a single key/value pair in the vault."""
    data = load_vault(password, vault_path)
    data[key] = value
    save_vault(data, password, vault_path)


def get_secret(key: str, password: str, vault_path: Optional[Path] = None) -> Optional[str]:
    """Retrieve a single value from the vault, or None if missing."""
    data = load_vault(password, vault_path)
    return data.get(key)


def delete_secret(key: str, password: str, vault_path: Optional[Path] = None) -> bool:
    """Remove a key from the vault. Returns True if it existed."""
    data = load_vault(password, vault_path)
    if key not in data:
        return False
    del data[key]
    save_vault(data, password, vault_path)
    return True


def list_keys(password: str, vault_path: Optional[Path] = None) -> list:
    """Return a sorted list of all keys stored in the vault."""
    data = load_vault(password, vault_path)
    return sorted(data.keys())
