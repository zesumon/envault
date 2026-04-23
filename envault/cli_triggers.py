"""CLI commands for managing triggers."""

from __future__ import annotations

import click

from .triggers import (
    VALID_EVENTS,
    add_trigger,
    clear_triggers,
    get_triggers,
    list_triggers,
    remove_trigger,
)
from .storage import get_vault_path


@click.group("trigger")
def cmd_trigger() -> None:
    """Manage key event triggers."""


@cmd_trigger.command("add")
@click.argument("key")
@click.argument("event")
@click.argument("command")
@click.option("--profile", default="default", show_default=True)
def trigger_add(key: str, event: str, command: str, profile: str) -> None:
    """Add a trigger command for KEY on EVENT."""
    vault_path = get_vault_path(profile)
    try:
        add_trigger(vault_path, key, event, command)
        click.echo(f"Trigger added: [{event}] {key} -> {command}")
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


@cmd_trigger.command("remove")
@click.argument("key")
@click.argument("event")
@click.argument("command")
@click.option("--profile", default="default", show_default=True)
def trigger_remove(key: str, event: str, command: str, profile: str) -> None:
    """Remove a specific trigger command."""
    vault_path = get_vault_path(profile)
    removed = remove_trigger(vault_path, key, event, command)
    if removed:
        click.echo(f"Trigger removed: [{event}] {key} -> {command}")
    else:
        click.echo("Trigger not found.")


@cmd_trigger.command("list")
@click.option("--profile", default="default", show_default=True)
@click.option("--key", default=None, help="Filter by key")
def trigger_list(profile: str, key: str) -> None:
    """List all triggers, optionally filtered by key."""
    vault_path = get_vault_path(profile)
    if key:
        data = {key: get_triggers(vault_path, key)}
    else:
        data = list_triggers(vault_path)
    if not data:
        click.echo("No triggers defined.")
        return
    for k, events in sorted(data.items()):
        for event, cmds in sorted(events.items()):
            for cmd in cmds:
                click.echo(f"{k}  [{event}]  {cmd}")


@cmd_trigger.command("clear")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def trigger_clear(key: str, profile: str) -> None:
    """Remove all triggers for KEY."""
    vault_path = get_vault_path(profile)
    clear_triggers(vault_path, key)
    click.echo(f"All triggers cleared for '{key}'.")


@cmd_trigger.command("events")
def trigger_events() -> None:
    """List valid trigger event names."""
    for ev in VALID_EVENTS:
        click.echo(ev)
