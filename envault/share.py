"""Share vault secrets as time-limited, password-protected export bundles."""

import json
import os
import time
from pathlib import Path
from typing import Optional

from envault.crypto import encrypt, decrypt
from envault.storage import load_vault, get_secret


def _get_shares_dir(vault_path: str) -> Path:
    return Path(vault_path).parent / "shares"


def create_share(
    vault_path: str,
    password: str,
    share_password: str,
    keys: list[str],
    ttl_seconds: int = 3600,
) -> str:
    """Create an encrypted share bundle for the given keys.

    Returns the share filename (stored under the vault's shares/ dir).
    """
    secrets = {}
    for key in keys:
        value = get_secret(vault_path, password, key)
        if value is None:
            raise KeyError(f"Key not found in vault: {key}")
        secrets[key] = value

    payload = json.dumps({
        "secrets": secrets,
        "expires_at": time.time() + ttl_seconds,
        "created_at": time.time(),
    })

    blob = encrypt(share_password, payload)

    shares_dir = _get_shares_dir(vault_path)
    shares_dir.mkdir(parents=True, exist_ok=True)

    slug = f"share_{int(time.time())}_{os.urandom(4).hex()}.enc"
    share_file = shares_dir / slug
    share_file.write_text(blob)
    return slug


def open_share(
    vault_path: str,
    share_name: str,
    share_password: str,
) -> dict[str, str]:
    """Decrypt and return secrets from a share bundle.

    Raises ValueError if the share has expired.
    Raises FileNotFoundError if the share doesn't exist.
    """
    share_file = _get_shares_dir(vault_path) / share_name
    if not share_file.exists():
        raise FileNotFoundError(f"Share not found: {share_name}")

    blob = share_file.read_text()
    payload = json.loads(decrypt(share_password, blob))

    if time.time() > payload["expires_at"]:
        raise ValueError("Share has expired")

    return payload["secrets"]


def list_shares(vault_path: str) -> list[str]:
    """Return sorted list of share bundle filenames."""
    shares_dir = _get_shares_dir(vault_path)
    if not shares_dir.exists():
        return []
    return sorted(p.name for p in shares_dir.glob("*.enc"))


def delete_share(vault_path: str, share_name: str) -> None:
    """Delete a share bundle by name."""
    share_file = _get_shares_dir(vault_path) / share_name
    if not share_file.exists():
        raise FileNotFoundError(f"Share not found: {share_name}")
    share_file.unlink()
