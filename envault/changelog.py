"""Changelog tracking for vault secrets.

Maintains a structured changelog of significant events across the vault,
aggregating changes from history, audit, and lifecycle modules into a
human-readable summary.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

CHANGELOG_FILE = "changelog.json"


def _get_changelog_path(vault_path: str) -> str:
    """Return path to the changelog file for the given vault."""
    vault_dir = os.path.dirname(vault_path)
    return os.path.join(vault_dir, CHANGELOG_FILE)


def _load_changelog(changelog_path: str) -> list:
    """Load changelog entries from disk, returning empty list if missing."""
    if not os.path.exists(changelog_path):
        return []
    with open(changelog_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_changelog(changelog_path: str, entries: list) -> None:
    """Persist changelog entries to disk."""
    with open(changelog_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)


def _now_iso() -> str:
    """Return current UTC time as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


def add_entry(
    vault_path: str,
    action: str,
    key: str,
    description: str,
    author: Optional[str] = None,
) -> dict:
    """Add a changelog entry for a key action.

    Args:
        vault_path: Path to the vault file.
        action: The action performed (e.g. 'set', 'delete', 'rotate').
        key: The secret key affected.
        description: Human-readable description of the change.
        author: Optional author/user identifier.

    Returns:
        The newly created changelog entry dict.
    """
    changelog_path = _get_changelog_path(vault_path)
    entries = _load_changelog(changelog_path)

    entry = {
        "timestamp": _now_iso(),
        "action": action,
        "key": key,
        "description": description,
    }
    if author:
        entry["author"] = author

    entries.append(entry)
    _save_changelog(changelog_path, entries)
    return entry


def get_entries(
    vault_path: str,
    key: Optional[str] = None,
    action: Optional[str] = None,
    limit: Optional[int] = None,
) -> list:
    """Retrieve changelog entries, optionally filtered.

    Args:
        vault_path: Path to the vault file.
        key: If provided, only return entries for this key.
        action: If provided, only return entries with this action.
        limit: If provided, return only the last N entries.

    Returns:
        List of matching changelog entry dicts, newest last.
    """
    changelog_path = _get_changelog_path(vault_path)
    entries = _load_changelog(changelog_path)

    if key is not None:
        entries = [e for e in entries if e.get("key") == key]
    if action is not None:
        entries = [e for e in entries if e.get("action") == action]
    if limit is not None:
        entries = entries[-limit:]

    return entries


def clear_changelog(vault_path: str) -> int:
    """Remove all changelog entries.

    Returns:
        Number of entries that were cleared.
    """
    changelog_path = _get_changelog_path(vault_path)
    entries = _load_changelog(changelog_path)
    count = len(entries)
    _save_changelog(changelog_path, [])
    return count


def summarise(vault_path: str) -> dict:
    """Return a summary of changelog activity.

    Returns:
        Dict with total entry count, unique keys touched, and action breakdown.
    """
    changelog_path = _get_changelog_path(vault_path)
    entries = _load_changelog(changelog_path)

    action_counts: dict = {}
    keys_touched: set = set()

    for entry in entries:
        action = entry.get("action", "unknown")
        action_counts[action] = action_counts.get(action, 0) + 1
        if entry.get("key"):
            keys_touched.add(entry["key"])

    return {
        "total": len(entries),
        "keys_touched": sorted(keys_touched),
        "actions": action_counts,
    }
