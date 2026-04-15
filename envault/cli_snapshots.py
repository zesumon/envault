"""CLI commands for vault snapshots."""

import click

from envault.cli import _get_password
from envault.snapshots import (
    list_snapshots,
    create_snapshot,
    restore_snapshot,
    delete_snapshot,
)


@click.group("snapshot")
def cmd_snapshot() -> None:
    """Manage vault snapshots."""


@cmd_snapshot.command("list")
@click.option("--vault-dir", default=None, hidden=True)
def snapshot_list(vault_dir: str) -> None:
    """List available snapshots."""
    snaps = list_snapshots(vault_dir=vault_dir)
    if not snaps:
        click.echo("No snapshots found.")
        return
    for name in snaps:
        click.echo(name)


@cmd_snapshot.command("create")
@click.option("--name", default=None, help="Optional snapshot name.")
@click.option("--vault-dir", default=None, hidden=True)
def snapshot_create(name: str, vault_dir: str) -> None:
    """Create a snapshot of the current vault."""
    password = _get_password(confirm=False)
    try:
        snap_name = create_snapshot(password, name=name, vault_dir=vault_dir)
        click.echo(f"Snapshot '{snap_name}' created.")
    except ValueError as exc:
        raise click.ClickException(str(exc))


@cmd_snapshot.command("restore")
@click.argument("name")
@click.option("--vault-dir", default=None, hidden=True)
def snapshot_restore(name: str, vault_dir: str) -> None:
    """Restore vault from a named snapshot."""
    password = _get_password(confirm=False)
    try:
        count = restore_snapshot(name, password, vault_dir=vault_dir)
        click.echo(f"Restored {count} key(s) from snapshot '{name}'.")
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))


@cmd_snapshot.command("delete")
@click.argument("name")
@click.option("--vault-dir", default=None, hidden=True)
def snapshot_delete(name: str, vault_dir: str) -> None:
    """Delete a named snapshot."""
    try:
        delete_snapshot(name, vault_dir=vault_dir)
        click.echo(f"Snapshot '{name}' deleted.")
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))
