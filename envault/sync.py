"""Sync logic: merge vault secrets with a .env file on disk."""

from pathlib import Path
from typing import Literal

from envault.export import import_from_file, export_to_file
from envault.storage import load_vault, save_vault, get_vault_path


ConflictStrategy = Literal["vault", "file", "skip"]


def sync_vault_to_file(
    password: str,
    env_path: Path,
    conflict: ConflictStrategy = "vault",
) -> dict[str, str]:
    """
    Sync secrets from the vault into a .env file.

    Args:
        password: Master password for decrypting the vault.
        env_path: Path to the target .env file.
        conflict: How to handle key conflicts — 'vault' prefers vault,
                  'file' prefers existing file values, 'skip' keeps both unchanged.

    Returns:
        The merged secrets dict that was written to the file.
    """
    vault = load_vault(get_vault_path(), password)
    file_secrets = import_from_file(env_path) if env_path.exists() else {}

    merged = _merge(vault, file_secrets, conflict)
    export_to_file(merged, env_path, overwrite=True)
    return merged


def sync_file_to_vault(
    password: str,
    env_path: Path,
    conflict: ConflictStrategy = "file",
) -> dict[str, str]:
    """
    Sync secrets from a .env file into the vault.

    Returns:
        The merged secrets dict that was saved to the vault.
    """
    vault_path = get_vault_path()
    vault = load_vault(vault_path, password)
    file_secrets = import_from_file(env_path)

    merged = _merge(file_secrets, vault, conflict)
    save_vault(vault_path, merged, password)
    return merged


def _merge(
    primary: dict[str, str],
    secondary: dict[str, str],
    conflict: ConflictStrategy,
) -> dict[str, str]:
    """Merge two secret dicts according to the conflict strategy."""
    result = dict(secondary)
    for key, value in primary.items():
        if key not in result:
            result[key] = value
        elif conflict == "vault" or conflict == "file":
            # primary wins when strategy matches its origin
            result[key] = value
        # else conflict == "skip": leave secondary value unchanged
    return result
