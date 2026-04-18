"""CLI commands for key priority management."""
import click
from pathlib import Path
from envault.priorities import (
    set_priority, get_priority, remove_priority,
    list_priorities, keys_by_priority, VALID_PRIORITIES,
)


@click.group("priority")
def cmd_priority():
    """Manage key priorities."""


@cmd_priority.command("set")
@click.argument("key")
@click.argument("priority", type=click.Choice(VALID_PRIORITIES))
@click.option("--vault", default=".envault/vault.enc", show_default=True)
def priority_set(key, priority, vault):
    """Set priority for a key."""
    try:
        set_priority(Path(vault), key, priority)
        click.echo(f"Priority for '{key}' set to '{priority}'.")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cmd_priority.command("get")
@click.argument("key")
@click.option("--vault", default=".envault/vault.enc", show_default=True)
def priority_get(key, vault):
    """Get priority for a key."""
    p = get_priority(Path(vault), key)
    if p is None:
        click.echo(f"No priority set for '{key}'.")
    else:
        click.echo(p)


@cmd_priority.command("remove")
@click.argument("key")
@click.option("--vault", default=".envault/vault.enc", show_default=True)
def priority_remove(key, vault):
    """Remove priority for a key."""
    removed = remove_priority(Path(vault), key)
    if removed:
        click.echo(f"Priority removed for '{key}'.")
    else:
        click.echo(f"No priority found for '{key}'.")


@cmd_priority.command("list")
@click.option("--vault", default=".envault/vault.enc", show_default=True)
@click.option("--filter", "filter_by", type=click.Choice(VALID_PRIORITIES), default=None)
def priority_list(vault, filter_by):
    """List all key priorities."""
    if filter_by:
        keys = keys_by_priority(Path(vault), filter_by)
        if not keys:
            click.echo(f"No keys with priority '{filter_by}'.")
        for k in keys:
            click.echo(f"{k}: {filter_by}")
    else:
        data = list_priorities(Path(vault))
        if not data:
            click.echo("No priorities set.")
        for k in sorted(data):
            click.echo(f"{k}: {data[k]}")
