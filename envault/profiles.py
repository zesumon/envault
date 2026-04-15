"""Profile management for envault — named sets of secrets (e.g. dev, staging, prod)."""

import json
from pathlib import Path
from typing import Optional

from envault.storage import get_vault_path, load_vault, save_vault


DEFAULT_PROFILE = "default"


def get_profiles_meta_path(vault_dir: Optional[Path] = None) -> Path:
    base = vault_dir or get_vault_path().parent
    return base / "profiles.json"


def list_profiles(vault_dir: Optional[Path] = None) -> list[str]:
    meta = get_profiles_meta_path(vault_dir)
    if not meta.exists():
        return [DEFAULT_PROFILE]
    data = json.loads(meta.read_text())
    profiles = data.get("profiles", [DEFAULT_PROFILE])
    if DEFAULT_PROFILE not in profiles:
        profiles.insert(0, DEFAULT_PROFILE)
    return profiles


def create_profile(name: str, vault_dir: Optional[Path] = None) -> None:
    if not name.isidentifier():
        raise ValueError(f"Invalid profile name: {name!r}. Use alphanumeric/underscore only.")
    meta = get_profiles_meta_path(vault_dir)
    profiles = list_profiles(vault_dir)
    if name in profiles:
        raise ValueError(f"Profile {name!r} already exists.")
    profiles.append(name)
    meta.parent.mkdir(parents=True, exist_ok=True)
    meta.write_text(json.dumps({"profiles": profiles}, indent=2))


def delete_profile(name: str, vault_dir: Optional[Path] = None) -> None:
    if name == DEFAULT_PROFILE:
        raise ValueError("Cannot delete the default profile.")
    meta = get_profiles_meta_path(vault_dir)
    profiles = list_profiles(vault_dir)
    if name not in profiles:
        raise KeyError(f"Profile {name!r} not found.")
    profiles.remove(name)
    meta.write_text(json.dumps({"profiles": profiles}, indent=2))
    # Remove the profile vault file if it exists
    vault_file = (vault_dir or get_vault_path().parent) / f"vault_{name}.enc"
    if vault_file.exists():
        vault_file.unlink()


def get_profile_vault_path(profile: str, vault_dir: Optional[Path] = None) -> Path:
    base = vault_dir or get_vault_path().parent
    if profile == DEFAULT_PROFILE:
        return get_vault_path() if vault_dir is None else base / "vault.enc"
    return base / f"vault_{profile}.enc"
