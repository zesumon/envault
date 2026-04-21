"""CLI commands for key lifecycle state management."""

import click

from envault.lifecycle import (
    VALID_STATES,
    get_lifecycle,
    keys_by_state,
    list_lifecycle,
    remove_lifecycle,
    set_lifecycle,
)
from envault.storage import get_vault_path


@click.group(name="lifecycle")
def cmd_lifecycle():
    """Manage key lifecycle states (active, deprecated, archived, draft)."""


@cmd_lifecycle.command("set")
@click.argument("key")
@click.argument("state", type=click.Choice(VALID_STATES))
@click.option("--profile", default="default", show_default=True)
def lifecycle_set(key, state, profile):
    """Set the lifecycle state of a key."""
    vault_path = get_vault_path(profile)
    try:
        set_lifecycle(vault_path, key, state)
        click.echo(f"Set lifecycle of '{key}' to '{state}'.")
    except ValueError as e:
        raise click.ClickException(str(e))


@cmd_lifecycle.command("get")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def lifecycle_get(key, profile):
    """Get the lifecycle state of a key."""
    vault_path = get_vault_path(profile)
    state = get_lifecycle(vault_path, key)
    if state is None:
        click.echo(f"No lifecycle state set for '{key}'.")
    else:
        click.echo(f"{key}: {state}")


@cmd_lifecycle.command("remove")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def lifecycle_remove(key, profile):
    """Remove the lifecycle state from a key."""
    vault_path = get_vault_path(profile)
    removed = remove_lifecycle(vault_path, key)
    if removed:
        click.echo(f"Removed lifecycle state for '{key}'.")
    else:
        click.echo(f"No lifecycle state found for '{key}'.")


@cmd_lifecycle.command("list")
@click.option("--profile", default="default", show_default=True)
@click.option("--state", type=click.Choice(VALID_STATES), default=None, help="Filter by state.")
def lifecycle_list(profile, state):
    """List all keys and their lifecycle states."""
    vault_path = get_vault_path(profile)
    if state:
        keys = keys_by_state(vault_path, state)
        if not keys:
            click.echo(f"No keys with state '{state}'.")
        else:
            for k in keys:
                click.echo(f"{k}: {state}")
    else:
        data = list_lifecycle(vault_path)
        if not data:
            click.echo("No lifecycle states defined.")
        else:
            for k, v in data.items():
                click.echo(f"{k}: {v}")
