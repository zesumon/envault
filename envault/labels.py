"""Key labeling — attach a short human-readable label/description to any secret key."""
from __future__ import annotations
import json
from pathlib import Path
from envault.storage import get_vault_path


def _get_labels_path(vault_path: Path) -> Path:
    return vault_path.parent / "labels.json"


def _load_labels(vault_path: Path) -> dict[str, str]:
    p = _get_labels_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_labels(vault_path: Path, data: dict[str, str]) -> None:
    p = _get_labels_path(vault_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, sort_keys=True))


def set_label(vault_path: Path, key: str, label: str) -> None:
    """Attach a label to *key*. Overwrites any existing label."""
    data = _load_labels(vault_path)
    data[key] = label
    _save_labels(vault_path, data)


def get_label(vault_path: Path, key: str) -> str | None:
    """Return the label for *key*, or None if not set."""
    return _load_labels(vault_path).get(key)


def remove_label(vault_path: Path, key: str) -> bool:
    """Remove the label for *key*. Returns True if a label existed."""
    data = _load_labels(vault_path)
    if key not in data:
        return False
    del data[key]
    _save_labels(vault_path, data)
    return True


def list_labels(vault_path: Path) -> dict[str, str]:
    """Return all key→label mappings, sorted by key."""
    return dict(sorted(_load_labels(vault_path).items()))
