"""Schema validation for vault keys."""
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Optional

SCHEMA_FILENAME = "schema.json"

VALID_TYPES = {"string", "integer", "boolean", "url", "email"}

TYPE_PATTERNS = {
    "integer": re.compile(r"^-?\d+$"),
    "boolean": re.compile(r"^(true|false|1|0)$", re.IGNORECASE),
    "url": re.compile(r"^https?://.+"),
    "email": re.compile(r"^[^@]+@[^@]+\.[^@]+$"),
}


def _get_schema_path(vault_path: Path) -> Path:
    return vault_path.parent / SCHEMA_FILENAME


def _load_schema(vault_path: Path) -> dict:
    p = _get_schema_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_schema(vault_path: Path, schema: dict) -> None:
    p = _get_schema_path(vault_path)
    p.write_text(json.dumps(schema, indent=2, sort_keys=True))


def set_schema(vault_path: Path, key: str, type_: str, required: bool = False, pattern: Optional[str] = None) -> None:
    if type_ not in VALID_TYPES:
        raise ValueError(f"Invalid type '{type_}'. Must be one of: {', '.join(sorted(VALID_TYPES))}")
    if pattern:
        re.compile(pattern)  # validate regex
    schema = _load_schema(vault_path)
    schema[key] = {"type": type_, "required": required}
    if pattern:
        schema[key]["pattern"] = pattern
    _save_schema(vault_path, schema)


def remove_schema(vault_path: Path, key: str) -> bool:
    schema = _load_schema(vault_path)
    if key not in schema:
        return False
    del schema[key]
    _save_schema(vault_path, schema)
    return True


def get_schema(vault_path: Path, key: str) -> Optional[dict]:
    return _load_schema(vault_path).get(key)


def list_schema(vault_path: Path) -> dict:
    return _load_schema(vault_path)


def validate_value(vault_path: Path, key: str, value: str) -> list[str]:
    """Return list of validation error messages (empty = valid)."""
    schema = _load_schema(vault_path)
    if key not in schema:
        return []
    rule = schema[key]
    errors = []
    type_ = rule.get("type", "string")
    if type_ in TYPE_PATTERNS:
        if not TYPE_PATTERNS[type_].match(value):
            errors.append(f"Value does not match type '{type_}'")
    if "pattern" in rule:
        if not re.match(rule["pattern"], value):
            errors.append(f"Value does not match pattern '{rule['pattern']}'")
    return errors


def validate_required(vault_path: Path, present_keys: set[str]) -> list[str]:
    """Return list of missing required keys."""
    schema = _load_schema(vault_path)
    return [k for k, v in schema.items() if v.get("required") and k not in present_keys]
