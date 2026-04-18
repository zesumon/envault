"""Key locking — prevent accidental modification of sensitive keys."""

import json
from pathlib import Path
from envault.storage import get_vault_path


def _get_locks_path(vault_path: Path) -> Path:
    return vault_path.parent / "locks.json"


def _load_locks(vault_path: Path) -> list:
    p = _get_locks_path(vault_path)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save_locks(vault_path: Path, locks: list) -> None:
    p = _get_locks_path(vault_path)
    p.write_text(json.dumps(sorted(set(locks)), indent=2))


def lock_key(vault_path: Path, key: str) -> None:
    """Lock a key so it cannot be modified or deleted."""
    from envault.storage import get_secret
    if get_secret(vault_path, key, password="") is None:
        # check key exists without password by peeking at raw vault
        pass
    locks = _load_locks(vault_path)
    if key not in locks:
        locks.append(key)
    _save_locks(vault_path, locks)


def unlock_key(vault_path: Path, key: str) -> bool:
    """Unlock a key. Returns True if it was locked, False otherwise."""
    locks = _load_locks(vault_path)
    if key not in locks:
        return False
    locks.remove(key)
    _save_locks(vault_path, locks)
    return True


def is_locked(vault_path: Path, key: str) -> bool:
    return key in _load_locks(vault_path)


def list_locks(vault_path: Path) -> list:
    return _load_locks(vault_path)


def assert_not_locked(vault_path: Path, key: str) -> None:
    if is_locked(vault_path, key):
        raise PermissionError(f"Key '{key}' is locked and cannot be modified.")
