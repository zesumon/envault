"""Template support for envault — save and apply named key scaffolds."""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

TEMPLATES_FILENAME = "templates.json"


def _get_templates_path(vault_dir: Path) -> Path:
    return vault_dir / TEMPLATES_FILENAME


def _load_templates(vault_dir: Path) -> Dict[str, List[str]]:
    path = _get_templates_path(vault_dir)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_templates(vault_dir: Path, data: Dict[str, List[str]]) -> None:
    path = _get_templates_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


_VALID_NAME = re.compile(r"^[a-zA-Z0-9_-]+$")


def list_templates(vault_dir: Path) -> List[str]:
    """Return sorted list of template names."""
    return sorted(_load_templates(vault_dir).keys())


def save_template(vault_dir: Path, name: str, keys: List[str]) -> None:
    """Save a named template with the given list of keys."""
    if not _VALID_NAME.match(name):
        raise ValueError(f"Invalid template name: {name!r}")
    if not keys:
        raise ValueError("Template must contain at least one key.")
    data = _load_templates(vault_dir)
    data[name] = sorted(set(keys))
    _save_templates(vault_dir, data)


def delete_template(vault_dir: Path, name: str) -> None:
    """Delete a template by name."""
    data = _load_templates(vault_dir)
    if name not in data:
        raise KeyError(f"Template not found: {name!r}")
    del data[name]
    _save_templates(vault_dir, data)


def get_template_keys(vault_dir: Path, name: str) -> List[str]:
    """Return the keys defined in a template."""
    data = _load_templates(vault_dir)
    if name not in data:
        raise KeyError(f"Template not found: {name!r}")
    return data[name]


def check_missing_keys(
    vault_dir: Path, name: str, present_keys: List[str]
) -> List[str]:
    """Return keys required by the template that are absent from present_keys."""
    required = get_template_keys(vault_dir, name)
    present = set(present_keys)
    return [k for k in required if k not in present]
