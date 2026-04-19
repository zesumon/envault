"""Key ratings — let users assign a 1-5 importance rating to secrets."""
from __future__ import annotations
import json
from pathlib import Path
from envault.storage import get_vault_path

VALID_RATINGS = {1, 2, 3, 4, 5}


def _get_ratings_path(vault_path: Path) -> Path:
    return vault_path.parent / "ratings.json"


def _load_ratings(vault_path: Path) -> dict:
    p = _get_ratings_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_ratings(vault_path: Path, data: dict) -> None:
    p = _get_ratings_path(vault_path)
    p.write_text(json.dumps(data, indent=2, sort_keys=True))


def set_rating(vault_path: Path, key: str, rating: int) -> None:
    """Assign a rating (1-5) to a key."""
    if rating not in VALID_RATINGS:
        raise ValueError(f"Rating must be 1-5, got {rating}")
    data = _load_ratings(vault_path)
    data[key] = rating
    _save_ratings(vault_path, data)


def get_rating(vault_path: Path, key: str) -> int | None:
    """Return the rating for a key, or None if not set."""
    return _load_ratings(vault_path).get(key)


def remove_rating(vault_path: Path, key: str) -> bool:
    """Remove rating for a key. Returns True if it existed."""
    data = _load_ratings(vault_path)
    if key not in data:
        return False
    del data[key]
    _save_ratings(vault_path, data)
    return True


def list_ratings(vault_path: Path) -> dict[str, int]:
    """Return all key->rating mappings sorted by key."""
    return dict(sorted(_load_ratings(vault_path).items()))
