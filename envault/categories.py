"""Category management for vault keys."""
import json
from pathlib import Path
from typing import Dict, List, Optional

VALID_CATEGORIES = {"database", "api", "auth", "storage", "network", "misc"}


def _get_categories_path(vault_path: Path) -> Path:
    return vault_path.parent / "categories.json"


def _load_categories(vault_path: Path) -> Dict[str, str]:
    p = _get_categories_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_categories(vault_path: Path, data: Dict[str, str]) -> None:
    p = _get_categories_path(vault_path)
    p.write_text(json.dumps(data, indent=2, sort_keys=True))


def set_category(vault_path: Path, key: str, category: str) -> None:
    from envault.storage import load_vault
    if category not in VALID_CATEGORIES:
        raise ValueError(f"Invalid category '{category}'. Choose from: {sorted(VALID_CATEGORIES)}")
    vault = load_vault(vault_path)
    if key not in vault:
        raise KeyError(f"Key '{key}' not found in vault")
    data = _load_categories(vault_path)
    data[key] = category
    _save_categories(vault_path, data)


def get_category(vault_path: Path, key: str) -> Optional[str]:
    return _load_categories(vault_path).get(key)


def remove_category(vault_path: Path, key: str) -> bool:
    data = _load_categories(vault_path)
    if key not in data:
        return False
    del data[key]
    _save_categories(vault_path, data)
    return True


def list_by_category(vault_path: Path, category: str) -> List[str]:
    data = _load_categories(vault_path)
    return sorted(k for k, v in data.items() if v == category)


def list_all_categories(vault_path: Path) -> Dict[str, str]:
    return _load_categories(vault_path)
