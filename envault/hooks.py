"""Pre/post command hooks for envault."""

import json
import os
from pathlib import Path
from typing import Callable, Dict, List, Optional

_VALID_EVENTS = {
    "pre-set", "post-set",
    "pre-delete", "post-delete",
    "pre-export", "post-export",
    "pre-import", "post-import",
}


def _get_hooks_path(vault_path: Path) -> Path:
    return vault_path.parent / "hooks.json"


def _load_hooks(vault_path: Path) -> Dict[str, List[str]]:
    p = _get_hooks_path(vault_path)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_hooks(vault_path: Path, data: Dict[str, List[str]]) -> None:
    p = _get_hooks_path(vault_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        json.dump(data, f, indent=2)


def list_hooks(vault_path: Path) -> Dict[str, List[str]]:
    """Return all registered hooks keyed by event name."""
    return _load_hooks(vault_path)


def add_hook(vault_path: Path, event: str, command: str) -> None:
    """Register a shell command to run on the given event."""
    if event not in _VALID_EVENTS:
        raise ValueError(f"Unknown event '{event}'. Valid events: {sorted(_VALID_EVENTS)}")
    data = _load_hooks(vault_path)
    cmds = data.setdefault(event, [])
    if command in cmds:
        raise ValueError(f"Hook '{command}' already registered for event '{event}'")
    cmds.append(command)
    _save_hooks(vault_path, data)


def remove_hook(vault_path: Path, event: str, command: str) -> None:
    """Remove a registered hook command for the given event."""
    data = _load_hooks(vault_path)
    cmds = data.get(event, [])
    if command not in cmds:
        raise KeyError(f"Hook '{command}' not found for event '{event}'")
    cmds.remove(command)
    if not cmds:
        del data[event]
    _save_hooks(vault_path, data)


def get_hooks(vault_path: Path, event: str) -> List[str]:
    """Return commands registered for a specific event."""
    return _load_hooks(vault_path).get(event, [])


def fire_hooks(vault_path: Path, event: str, env: Optional[Dict[str, str]] = None) -> List[str]:
    """Run all hooks for an event. Returns list of commands that were executed."""
    import subprocess
    commands = get_hooks(vault_path, event)
    executed = []
    merged_env = {**os.environ, **(env or {})}
    for cmd in commands:
        subprocess.run(cmd, shell=True, env=merged_env, check=False)
        executed.append(cmd)
    return executed
