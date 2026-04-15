"""Search/filter secrets within a vault by key pattern or value presence."""

from __future__ import annotations

import fnmatch
from typing import Optional

from .storage import load_vault, get_vault_path
from .crypto import decrypt


def search_keys(
    password: str,
    pattern: str,
    *,
    profile: str = "default",
    vault_path: Optional[str] = None,
) -> list[str]:
    """Return keys matching a glob-style pattern (case-insensitive)."""
    path = vault_path or get_vault_path(profile)
    vault = load_vault(path)
    pattern_lower = pattern.lower()
    matched = [
        key
        for key in vault
        if fnmatch.fnmatch(key.lower(), pattern_lower)
    ]
    return sorted(matched)


def search_values(
    password: str,
    substring: str,
    *,
    profile: str = "default",
    vault_path: Optional[str] = None,
) -> list[tuple[str, str]]:
    """Return (key, value) pairs whose decrypted value contains *substring*."""
    path = vault_path or get_vault_path(profile)
    vault = load_vault(path)
    results: list[tuple[str, str]] = []
    sub_lower = substring.lower()
    for key, blob in vault.items():
        try:
            value = decrypt(blob, password)
        except Exception:
            continue
        if sub_lower in value.lower():
            results.append((key, value))
    return sorted(results, key=lambda t: t[0])


def list_keys(
    password: str,
    *,
    profile: str = "default",
    vault_path: Optional[str] = None,
) -> list[str]:
    """Return all keys stored in the vault, sorted alphabetically."""
    path = vault_path or get_vault_path(profile)
    vault = load_vault(path)
    return sorted(vault.keys())
