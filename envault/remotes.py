"""Remote vault registry — store and retrieve named remote endpoints."""

import json
import re
from pathlib import Path
from typing import Optional

REMOTE_NAME_RE = re.compile(r'^[a-zA-Z0-9_-]+$')


def _get_remotes_path(vault_dir: Path) -> Path:
    return vault_dir / ".envault" / "remotes.json"


def _load_remotes(vault_dir: Path) -> dict:
    path = _get_remotes_path(vault_dir)
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def _save_remotes(vault_dir: Path, data: dict) -> None:
    path = _get_remotes_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def list_remotes(vault_dir: Path) -> list[dict]:
    """Return list of {name, url} dicts sorted by name."""
    remotes = _load_remotes(vault_dir)
    return sorted(
        [{"name": k, "url": v} for k, v in remotes.items()],
        key=lambda r: r["name"],
    )


def add_remote(vault_dir: Path, name: str, url: str) -> None:
    """Register a named remote URL."""
    if not REMOTE_NAME_RE.match(name):
        raise ValueError(f"Invalid remote name '{name}'. Use letters, digits, _ or -.")
    if not url.strip():
        raise ValueError("Remote URL must not be empty.")
    remotes = _load_remotes(vault_dir)
    if name in remotes:
        raise KeyError(f"Remote '{name}' already exists. Use update_remote to change it.")
    remotes[name] = url.strip()
    _save_remotes(vault_dir, remotes)


def update_remote(vault_dir: Path, name: str, url: str) -> None:
    """Update the URL of an existing remote."""
    if not url.strip():
        raise ValueError("Remote URL must not be empty.")
    remotes = _load_remotes(vault_dir)
    if name not in remotes:
        raise KeyError(f"Remote '{name}' not found.")
    remotes[name] = url.strip()
    _save_remotes(vault_dir, remotes)


def remove_remote(vault_dir: Path, name: str) -> None:
    """Delete a named remote."""
    remotes = _load_remotes(vault_dir)
    if name not in remotes:
        raise KeyError(f"Remote '{name}' not found.")
    del remotes[name]
    _save_remotes(vault_dir, remotes)


def get_remote(vault_dir: Path, name: str) -> Optional[str]:
    """Return the URL for a named remote, or None if not found."""
    return _load_remotes(vault_dir).get(name)
