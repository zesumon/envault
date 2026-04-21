"""Constraints: attach validation rules (regex, min/max length) to secret keys."""

import json
import re
from pathlib import Path
from typing import Optional


def _get_constraints_path(vault_path: Path) -> Path:
    return vault_path.parent / "constraints.json"


def _load_constraints(vault_path: Path) -> dict:
    p = _get_constraints_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_constraints(vault_path: Path, data: dict) -> None:
    p = _get_constraints_path(vault_path)
    p.write_text(json.dumps(data, indent=2, sort_keys=True))


VALID_TYPES = {"regex", "min_length", "max_length"}


def set_constraint(vault_path: Path, key: str, constraint_type: str, value: str) -> None:
    """Attach a constraint to a key. constraint_type must be one of VALID_TYPES."""
    if constraint_type not in VALID_TYPES:
        raise ValueError(f"Invalid constraint type '{constraint_type}'. Choose from: {sorted(VALID_TYPES)}")
    if constraint_type in ("min_length", "max_length"):
        try:
            int(value)
        except ValueError:
            raise ValueError(f"Value for '{constraint_type}' must be an integer.")
    data = _load_constraints(vault_path)
    if key not in data:
        data[key] = {}
    data[key][constraint_type] = value
    _save_constraints(vault_path, data)


def remove_constraint(vault_path: Path, key: str, constraint_type: str) -> bool:
    data = _load_constraints(vault_path)
    if key not in data or constraint_type not in data[key]:
        return False
    del data[key][constraint_type]
    if not data[key]:
        del data[key]
    _save_constraints(vault_path, data)
    return True


def get_constraints(vault_path: Path, key: str) -> dict:
    return _load_constraints(vault_path).get(key, {})


def list_constraints(vault_path: Path) -> dict:
    return _load_constraints(vault_path)


def validate_value(vault_path: Path, key: str, value: str) -> list[str]:
    """Validate a value against all constraints for a key. Returns list of error messages."""
    errors = []
    constraints = get_constraints(vault_path, key)
    if "regex" in constraints:
        pattern = constraints["regex"]
        if not re.fullmatch(pattern, value):
            errors.append(f"Value does not match required pattern: {pattern}")
    if "min_length" in constraints:
        min_len = int(constraints["min_length"])
        if len(value) < min_len:
            errors.append(f"Value is too short (min {min_len} chars, got {len(value)})")
    if "max_length" in constraints:
        max_len = int(constraints["max_length"])
        if len(value) > max_len:
            errors.append(f"Value is too long (max {max_len} chars, got {len(value)})")
    return errors
