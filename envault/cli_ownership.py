"""CLI commands for key ownership management."""

from __future__ import annotations

import click

from envault.ownership import (
    get_owner,
    list_all_ownership,
    list_owned_keys,
    remove_owner,
    set_owner,
)
from envault.storage import get_vault_path


@click.group("ownership")
def cmd_ownership():
    """Manage key ownership."""


@cmd_ownership.command("set")
@click.argument("key")
@click.argument("owner")
@click.option("--vault", default=None, help="Path to vault file.")
def ownership_set(key: str, owner: str, vault):
    """Assign OWNER to KEY."""
    vp = get_vault_path(vault)
    try:
        set_owner(vp, key, owner)
        click.echo(f"Owner of '{key}' set to '{owner}'.")
    except ValueError as exc:
        raise click.ClickException(str(exc))


@cmd_ownership.command("get")
@click.argument("key")
@click.option("--vault", default=None, help="Path to vault file.")
def ownership_get(key: str, vault):
    """Show the owner of KEY."""
    vp = get_vault_path(vault)
    owner = get_owner(vp, key)
    if owner is None:
        click.echo(f"No owner set for '{key}'.")
    else:
        click.echo(owner)


@cmd_ownership.command("remove")
@click.argument("key")
@click.option("--vault", default=None, help="Path to vault file.")
def ownership_remove(key: str, vault):
    """Remove ownership record for KEY."""
    vp = get_vault_path(vault)
    removed = remove_owner(vp, key)
    if removed:
        click.echo(f"Ownership record for '{key}' removed.")
    else:
        click.echo(f"No ownership record found for '{key}'.")


@cmd_ownership.command("list")
@click.option("--owner", default=None, help="Filter by owner name.")
@click.option("--vault", default=None, help="Path to vault file.")
def ownership_list(owner, vault):
    """List ownership records, optionally filtered by owner."""
    vp = get_vault_path(vault)
    if owner:
        keys = list_owned_keys(vp, owner)
        if not keys:
            click.echo(f"No keys owned by '{owner}'.")
        else:
            for k in keys:
                click.echo(k)
    else:
        data = list_all_ownership(vp)
        if not data:
            click.echo("No ownership records.")
        else:
            for k in sorted(data):
                click.echo(f"{k}: {data[k]}")
