"""Key aliasing — map short names to full secret keys."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envault.storage import get_vault_path


def _get_aliases_path(vault_path: Path) -> Path:
    return vault_path.parent / "aliases.json"


def _load_aliases(vault_path: Path) -> dict[str, str]:
    p = _get_aliases_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_aliases(vault_path: Path, aliases: dict[str, str]) -> None:
    p = _get_aliases_path(vault_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(aliases, indent=2, sort_keys=True))


def add_alias(vault_path: Path, alias: str, key: str) -> None:
    """Register *alias* as a short name for *key*."""
    if not alias or not alias.isidentifier():
        raise ValueError(f"Invalid alias name: {alias!r}")
    aliases = _load_aliases(vault_path)
    if alias in aliases:
        raise ValueError(f"Alias {alias!r} already exists (points to {aliases[alias]!r})")
    aliases[alias] = key
    _save_aliases(vault_path, aliases)


def remove_alias(vault_path: Path, alias: str) -> None:
    """Remove an existing alias."""
    aliases = _load_aliases(vault_path)
    if alias not in aliases:
        raise KeyError(f"Alias {alias!r} not found")
    del aliases[alias]
    _save_aliases(vault_path, aliases)


def resolve_alias(vault_path: Path, alias: str) -> Optional[str]:
    """Return the key that *alias* points to, or None if not found."""
    return _load_aliases(vault_path).get(alias)


def list_aliases(vault_path: Path) -> dict[str, str]:
    """Return all aliases as {alias: key} sorted by alias name."""
    return dict(sorted(_load_aliases(vault_path).items()))


def update_alias(vault_path: Path, alias: str, new_key: str) -> None:
    """Point an existing alias at a different key."""
    aliases = _load_aliases(vault_path)
    if alias not in aliases:
        raise KeyError(f"Alias {alias!r} not found")
    aliases[alias] = new_key
    _save_aliases(vault_path, aliases)
