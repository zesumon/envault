"""CLI commands for audit log inspection."""

import click
from pathlib import Path
from typing import Optional

from envault.audit import read_events, clear_audit_log, get_audit_path


@click.command("audit")
@click.option("--vault-dir", default=None, help="Custom vault directory path.")
@click.option("--tail", default=0, type=int, help="Show last N events (0 = all).")
@click.option("--action", default=None, help="Filter by action (set/get/delete).")
def cmd_audit(vault_dir: Optional[str], tail: int, action: Optional[str]) -> None:
    """Display the audit log of vault operations."""
    vdir = Path(vault_dir) if vault_dir else None
    events = read_events(vault_dir=vdir)

    if action:
        events = [e for e in events if e.get("action") == action]

    if tail > 0:
        events = events[-tail:]

    if not events:
        click.echo("No audit events found.")
        return

    for e in events:
        click.echo(f"[{e.get('timestamp', '?')}] {e.get('action', '?'):8s} {e.get('key', '?')}")


@click.command("audit-clear")
@click.option("--vault-dir", default=None, help="Custom vault directory path.")
@click.confirmation_option(prompt="Are you sure you want to clear the audit log?")
def cmd_audit_clear(vault_dir: Optional[str]) -> None:
    """Clear the entire audit log."""
    vdir = Path(vault_dir) if vault_dir else None
    clear_audit_log(vault_dir=vdir)
    click.echo("Audit log cleared.")
