"""CLI commands for per-key change history."""

from __future__ import annotations

import click

from envault.history import (
    all_keys_with_history,
    clear_key_history,
    get_key_history,
)
from envault.storage import get_vault_path


@click.group("history")
def cmd_history() -> None:
    """View and manage per-key change history."""


@cmd_history.command("show")
@click.argument("key")
@click.option("--tail", "-n", default=0, help="Show only the last N entries (0 = all).")
def history_show(key: str, tail: int) -> None:
    """Show change history for KEY."""
    vault_path = get_vault_path()
    records = get_key_history(vault_path, key)
    if not records:
        click.echo(f"No history found for '{key}'.")
        return
    if tail > 0:
        records = records[-tail:]
    for rec in records:
        preview = f"  preview={rec['preview']}" if "preview" in rec else ""
        click.echo(f"{rec['timestamp']}  {rec['action']}{preview}")


@cmd_history.command("list")
def history_list() -> None:
    """List all keys that have recorded history."""
    vault_path = get_vault_path()
    keys = all_keys_with_history(vault_path)
    if not keys:
        click.echo("No history recorded yet.")
        return
    for k in keys:
        click.echo(k)


@cmd_history.command("clear")
@click.argument("key")
@click.confirmation_option(prompt="Clear all history for this key?")
def history_clear(key: str) -> None:
    """Delete all history records for KEY."""
    vault_path = get_vault_path()
    count = clear_key_history(vault_path, key)
    click.echo(f"Cleared {count} record(s) for '{key}'.")
