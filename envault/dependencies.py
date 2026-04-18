"""Track dependencies between keys (key A depends on key B)."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List

from envault.storage import get_vault_path


def _get_deps_path(vault_path: Path) -> Path:
    return vault_path.parent / "dependencies.json"


def _load_deps(vault_path: Path) -> Dict[str, List[str]]:
    p = _get_deps_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_deps(vault_path: Path, data: Dict[str, List[str]]) -> None:
    _get_deps_path(vault_path).write_text(json.dumps(data, indent=2))


def add_dependency(vault_path: Path, key: str, depends_on: str) -> None:
    """Record that `key` depends on `depends_on`."""
    from envault.storage import load_vault
    vault = load_vault(vault_path, password=None)  # just check key existence via raw load
    # We don't decrypt here — just track metadata
    data = _load_deps(vault_path)
    deps = data.setdefault(key, [])
    if depends_on not in deps:
        deps.append(depends_on)
        deps.sort()
    _save_deps(vault_path, data)


def remove_dependency(vault_path: Path, key: str, depends_on: str) -> bool:
    data = _load_deps(vault_path)
    deps = data.get(key, [])
    if depends_on not in deps:
        return False
    deps.remove(depends_on)
    if not deps:
        del data[key]
    _save_deps(vault_path, data)
    return True


def get_dependencies(vault_path: Path, key: str) -> List[str]:
    return _load_deps(vault_path).get(key, [])


def get_dependents(vault_path: Path, key: str) -> List[str]:
    """Return keys that depend on `key`."""
    data = _load_deps(vault_path)
    return sorted(k for k, deps in data.items() if key in deps)


def list_all_dependencies(vault_path: Path) -> Dict[str, List[str]]:
    return dict(_load_deps(vault_path))


def clear_dependencies(vault_path: Path, key: str) -> None:
    data = _load_deps(vault_path)
    data.pop(key, None)
    _save_deps(vault_path, data)
