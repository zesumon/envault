"""Per-key notes/annotations for vault secrets."""

import json
from pathlib import Path
from envault.storage import get_vault_path


def _get_notes_path(vault_path: Path) -> Path:
    return vault_path.parent / "notes.json"


def _load_notes(vault_path: Path) -> dict:
    p = _get_notes_path(vault_path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save_notes(vault_path: Path, notes: dict) -> None:
    p = _get_notes_path(vault_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(notes, indent=2, sort_keys=True))


def set_note(vault_path: Path, key: str, note: str) -> None:
    """Attach a note to a secret key."""
    notes = _load_notes(vault_path)
    notes[key] = note
    _save_notes(vault_path, notes)


def get_note(vault_path: Path, key: str) -> str | None:
    """Return the note for a key, or None if not set."""
    return _load_notes(vault_path).get(key)


def delete_note(vault_path: Path, key: str) -> bool:
    """Remove a note. Returns True if it existed, False otherwise."""
    notes = _load_notes(vault_path)
    if key not in notes:
        return False
    del notes[key]
    _save_notes(vault_path, notes)
    return True


def list_notes(vault_path: Path) -> dict:
    """Return all key -> note mappings."""
    return dict(_load_notes(vault_path))


def clear_notes(vault_path: Path) -> int:
    """Remove all notes. Returns count of deleted notes."""
    notes = _load_notes(vault_path)
    count = len(notes)
    _save_notes(vault_path, {})
    return count
