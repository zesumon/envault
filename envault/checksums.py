"""Track checksums of secret values to detect external tampering."""

import hashlib
import json
from pathlib import Path
from typing import Optional

from envault.storage import get_vault_path, load_vault


def _get_checksums_path(vault_path: Path) -> Path:
    return vault_path.parent / "checksums.json"


def _load_checksums(vault_path: Path) -> dict:
    p = _get_checksums_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_checksums(vault_path: Path, data: dict) -> None:
    p = _get_checksums_path(vault_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, sort_keys=True))


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def record_checksum(vault_path: Path, key: str, value: str) -> str:
    data = _load_checksums(vault_path)
    digest = _hash(value)
    data[key] = digest
    _save_checksums(vault_path, data)
    return digest


def get_checksum(vault_path: Path, key: str) -> Optional[str]:
    return _load_checksums(vault_path).get(key)


def remove_checksum(vault_path: Path, key: str) -> None:
    data = _load_checksums(vault_path)
    data.pop(key, None)
    _save_checksums(vault_path, data)


def verify_checksum(vault_path: Path, key: str, value: str) -> bool:
    """Return True if value matches recorded checksum."""
    stored = get_checksum(vault_path, key)
    if stored is None:
        return False
    return stored == _hash(value)


def verify_all(vault_path: Path, password: str) -> dict:
    """Return dict of key -> bool for all keys in vault."""
    from envault.storage import load_vault, get_secret
    results = {}
    data = _load_checksums(vault_path)
    for key in data:
        val = get_secret(vault_path, key, password)
        if val is None:
            results[key] = False
        else:
            results[key] = verify_checksum(vault_path, key, val)
    return results
