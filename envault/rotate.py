"""Key rotation: re-encrypt vault secrets under a new password."""

from __future__ import annotations

from typing import Optional

from envault.storage import load_vault, save_vault
from envault.audit import log_event


def rotate_password(
    vault_path: str,
    old_password: str,
    new_password: str,
    profile: str = "default",
) -> int:
    """Re-encrypt every secret in the vault under *new_password*.

    Returns the number of secrets that were rotated.
    Raises ValueError if the old password is wrong (load_vault will raise).
    """
    secrets = load_vault(vault_path, old_password)

    if not secrets:
        return 0

    # save_vault encrypts all values with the new password
    save_vault(vault_path, new_password, secrets)

    count = len(secrets)
    log_event(
        vault_path,
        action="rotate",
        key="*",
        profile=profile,
        detail=f"{count} secret(s) re-encrypted",
    )
    return count


def rotate_dry_run(
    vault_path: str,
    old_password: str,
) -> Optional[list[str]]:
    """Return the list of keys that *would* be rotated, without writing anything.

    Returns None if the vault does not exist yet.
    Raises ValueError / InvalidToken if the password is wrong.
    """
    try:
        secrets = load_vault(vault_path, old_password)
    except FileNotFoundError:
        return None
    return list(secrets.keys())
