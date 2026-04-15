"""CLI commands for managing envault hooks."""

import click
from pathlib import Path

from envault.storage import get_vault_path
from envault.hooks import add_hook, remove_hook, list_hooks, _VALID_EVENTS


@click.group("hook")
def cmd_hook():
    """Manage pre/post command hooks."""


@cmd_hook.command("list")
@click.option("--vault-dir", default=None, hidden=True)
def hook_list(vault_dir):
    """List all registered hooks."""
    vault_path = get_vault_path(vault_dir)
    hooks = list_hooks(vault_path)
    if not hooks:
        click.echo("No hooks registered.")
        return
    for event in sorted(hooks):
        click.echo(f"[{event}]")
        for cmd in hooks[event]:
            click.echo(f"  {cmd}")


@cmd_hook.command("add")
@click.argument("event")
@click.argument("command")
@click.option("--vault-dir", default=None, hidden=True)
def hook_add(event, command, vault_dir):
    """Register a COMMAND to run on EVENT."""
    vault_path = get_vault_path(vault_dir)
    try:
        add_hook(vault_path, event, command)
        click.echo(f"Hook added: [{event}] -> {command}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cmd_hook.command("remove")
@click.argument("event")
@click.argument("command")
@click.option("--vault-dir", default=None, hidden=True)
def hook_remove(event, command, vault_dir):
    """Remove a registered hook COMMAND for EVENT."""
    vault_path = get_vault_path(vault_dir)
    try:
        remove_hook(vault_path, event, command)
        click.echo(f"Hook removed: [{event}] -> {command}")
    except (KeyError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cmd_hook.command("events")
def hook_events():
    """List all valid hook event names."""
    for event in sorted(_VALID_EVENTS):
        click.echo(event)
