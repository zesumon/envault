"""Environment-level metadata (e.g. dev, staging, prod) for vault profiles."""

import json
from pathlib import Path

VALID_ENVS = {"development", "staging", "production", "test", "local"}


def _get_envs_path(vault_dir: Path) -> Path:
    return vault_dir / ".envault" / "environments.json"


def _load_envs(vault_dir: Path) -> dict:
    p = _get_envs_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_envs(vault_dir: Path, data: dict) -> None:
    p = _get_envs_path(vault_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, sort_keys=True))


def set_environment(vault_dir: Path, profile: str, environment: str) -> None:
    """Associate a profile with an environment tier."""
    if environment not in VALID_ENVS:
        raise ValueError(f"Invalid environment '{environment}'. Choose from: {sorted(VALID_ENVS)}")
    data = _load_envs(vault_dir)
    data[profile] = environment
    _save_envs(vault_dir, data)


def get_environment(vault_dir: Path, profile: str) -> str | None:
    """Return the environment tier for a profile, or None."""
    return _load_envs(vault_dir).get(profile)


def remove_environment(vault_dir: Path, profile: str) -> bool:
    """Remove environment association. Returns True if it existed."""
    data = _load_envs(vault_dir)
    if profile not in data:
        return False
    del data[profile]
    _save_envs(vault_dir, data)
    return True


def list_environments(vault_dir: Path) -> dict:
    """Return mapping of profile -> environment."""
    return dict(sorted(_load_envs(vault_dir).items()))
