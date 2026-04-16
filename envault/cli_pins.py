"""CLI commands for managing pinned secrets."""

import click
from envault.storage import get_vault_path
from envault.pins import pin_key, unpin_key, is_pinned, list_pins


@click.group("pin")
def cmd_pin():
    """Pin secrets to protect them from modification or deletion."""


@cmd_pin.command("add")
@click.argument("key")
@click.option("--vault", default=None, help="Path to vault file")
def pin_add(key, vault):
    """Pin a secret KEY."""
    vp = get_vault_path(vault)
    try:
        pin_key(vp, key)
        click.echo(f"Pinned '{key}'.")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@cmd_pin.command("remove")
@click.argument("key")
@click.option("--vault", default=None, help="Path to vault file")
def pin_remove(key, vault):
    """Unpin a secret KEY."""
    vp = get_vault_path(vault)
    try:
        unpin_key(vp, key)
        click.echo(f"Unpinned '{key}'.")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@cmd_pin.command("list")
@click.option("--vault", default=None, help="Path to vault file")
def pin_list(vault):
    """List all pinned secrets."""
    vp = get_vault_path(vault)
    pins = list_pins(vp)
    if not pins:
        click.echo("No pinned secrets.")
    else:
        for k in pins:
            click.echo(k)


@cmd_pin.command("check")
@click.argument("key")
@click.option("--vault", default=None, help="Path to vault file")
def pin_check(key, vault):
    """Check whether KEY is pinned."""
    vp = get_vault_path(vault)
    if is_pinned(vp, key):
        click.echo(f"'{key}' is pinned.")
    else:
        click.echo(f"'{key}' is not pinned.")
