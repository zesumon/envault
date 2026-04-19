"""Workflow sequences: run multiple envault operations as a named batch."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any


def _get_workflows_path(vault_path: Path) -> Path:
    return vault_path.parent / "workflows.json"


def _load_workflows(vault_path: Path) -> dict[str, Any]:
    p = _get_workflows_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_workflows(vault_path: Path, data: dict[str, Any]) -> None:
    p = _get_workflows_path(vault_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def list_workflows(vault_path: Path) -> list[str]:
    return sorted(_load_workflows(vault_path).keys())


def save_workflow(vault_path: Path, name: str, steps: list[str]) -> None:
    if not name.replace("-", "").replace("_", "").isalnum():
        raise ValueError(f"Invalid workflow name: {name!r}")
    if not steps:
        raise ValueError("Workflow must have at least one step.")
    data = _load_workflows(vault_path)
    data[name] = {"steps": steps}
    _save_workflows(vault_path, data)


def get_workflow(vault_path: Path, name: str) -> list[str] | None:
    data = _load_workflows(vault_path)
    entry = data.get(name)
    return entry["steps"] if entry else None


def delete_workflow(vault_path: Path, name: str) -> bool:
    data = _load_workflows(vault_path)
    if name not in data:
        return False
    del data[name]
    _save_workflows(vault_path, data)
    return True


def rename_workflow(vault_path: Path, old: str, new: str) -> None:
    data = _load_workflows(vault_path)
    if old not in data:
        raise KeyError(f"Workflow not found: {old!r}")
    if new in data:
        raise ValueError(f"Workflow already exists: {new!r}")
    data[new] = data.pop(old)
    _save_workflows(vault_path, data)
