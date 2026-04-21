"""Bookmarks: save named positions/contexts for quick vault navigation."""

import json
from pathlib import Path
from typing import Optional


def _get_bookmarks_path(vault_path: Path) -> Path:
    return vault_path.parent / "bookmarks.json"


def _load_bookmarks(vault_path: Path) -> dict:
    p = _get_bookmarks_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_bookmarks(vault_path: Path, data: dict) -> None:
    p = _get_bookmarks_path(vault_path)
    p.write_text(json.dumps(data, indent=2, sort_keys=True))


def add_bookmark(vault_path: Path, name: str, key: str, note: str = "") -> None:
    """Bookmark a key under a given name."""
    if not name.replace("-", "").replace("_", "").isalnum():
        raise ValueError(f"Invalid bookmark name: {name!r}")
    data = _load_bookmarks(vault_path)
    data[name] = {"key": key, "note": note}
    _save_bookmarks(vault_path, data)


def remove_bookmark(vault_path: Path, name: str) -> None:
    """Remove a bookmark by name."""
    data = _load_bookmarks(vault_path)
    if name not in data:
        raise KeyError(f"Bookmark not found: {name!r}")
    del data[name]
    _save_bookmarks(vault_path, data)


def get_bookmark(vault_path: Path, name: str) -> Optional[dict]:
    """Return bookmark dict or None."""
    return _load_bookmarks(vault_path).get(name)


def list_bookmarks(vault_path: Path) -> list[dict]:
    """Return sorted list of bookmarks as dicts with name/key/note."""
    data = _load_bookmarks(vault_path)
    return [
        {"name": name, "key": v["key"], "note": v.get("note", "")}
        for name, v in sorted(data.items())
    ]


def resolve_bookmark(vault_path: Path, name: str) -> Optional[str]:
    """Return the key a bookmark points to, or None."""
    entry = get_bookmark(vault_path, name)
    return entry["key"] if entry else None
