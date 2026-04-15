"""Diff utilities for comparing vault state against a .env file."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from envault.export import parse_dotenv
from envault.storage import load_vault, get_secret


@dataclass
class DiffEntry:
    key: str
    status: str  # 'added' | 'removed' | 'changed' | 'unchanged'
    vault_value: Optional[str] = None
    file_value: Optional[str] = None


def diff_vault_vs_file(
    vault_path: str,
    dotenv_path: str,
    password: str,
    show_unchanged: bool = False,
) -> List[DiffEntry]:
    """Compare vault secrets against a .env file and return diff entries."""
    vault_data = load_vault(vault_path, password)
    vault_secrets: Dict[str, str] = vault_data.get("secrets", {})

    try:
        with open(dotenv_path, "r", encoding="utf-8") as fh:
            file_secrets = parse_dotenv(fh.read())
    except FileNotFoundError:
        file_secrets = {}

    all_keys = set(vault_secrets) | set(file_secrets)
    entries: List[DiffEntry] = []

    for key in sorted(all_keys):
        in_vault = key in vault_secrets
        in_file = key in file_secrets

        if in_vault and not in_file:
            entries.append(DiffEntry(key=key, status="removed", vault_value=vault_secrets[key]))
        elif in_file and not in_vault:
            entries.append(DiffEntry(key=key, status="added", file_value=file_secrets[key]))
        elif vault_secrets[key] != file_secrets[key]:
            entries.append(
                DiffEntry(
                    key=key,
                    status="changed",
                    vault_value=vault_secrets[key],
                    file_value=file_secrets[key],
                )
            )
        elif show_unchanged:
            entries.append(
                DiffEntry(
                    key=key,
                    status="unchanged",
                    vault_value=vault_secrets[key],
                    file_value=file_secrets[key],
                )
            )

    return entries


def format_diff(entries: List[DiffEntry], hide_values: bool = False) -> str:
    """Render diff entries as a human-readable string."""
    if not entries:
        return "No differences found."

    lines = []
    symbols = {"added": "+", "removed": "-", "changed": "~", "unchanged": " "}

    for entry in entries:
        sym = symbols[entry.status]
        if hide_values or entry.status == "unchanged":
            lines.append(f"  {sym} {entry.key}")
        elif entry.status == "added":
            lines.append(f"  {sym} {entry.key}={entry.file_value}")
        elif entry.status == "removed":
            lines.append(f"  {sym} {entry.key}={entry.vault_value}")
        elif entry.status == "changed":
            lines.append(f"  {sym} {entry.key}: vault={entry.vault_value!r} file={entry.file_value!r}")

    return "\n".join(lines)
