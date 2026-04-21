"""CLI commands for managing key watchers."""
import os

import click

from envault.storage import get_vault_path
from envault.watchers import (
    add_watcher,
    clear_watchers,
    get_watchers,
    list_all_watchers,
    remove_watcher,
)


@click.group(name="watcher")
def cmd_watcher():
    """Manage watchers for secret keys."""


@cmd_watcher.command("add")
@click.argument("key")
@click.argument("watcher")
@click.option("--profile", default="default", show_default=True)
def watcher_add(key: str, watcher: str, profile: str):
    """Subscribe WATCHER to changes on KEY."""
    vault_path = get_vault_path(profile)
    try:
        add_watcher(vault_path, key, watcher)
        click.echo(f"Watcher '{watcher}' added to key '{key}'.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@cmd_watcher.command("remove")
@click.argument("key")
@click.argument("watcher")
@click.option("--profile", default="default", show_default=True)
def watcher_remove(key: str, watcher: str, profile: str):
    """Unsubscribe WATCHER from KEY."""
    vault_path = get_vault_path(profile)
    removed = remove_watcher(vault_path, key, watcher)
    if removed:
        click.echo(f"Watcher '{watcher}' removed from key '{key}'.")
    else:
        click.echo(f"Watcher '{watcher}' was not subscribed to '{key}'.")


@cmd_watcher.command("list")
@click.argument("key", required=False)
@click.option("--profile", default="default", show_default=True)
def watcher_list(key: str | None, profile: str):
    """List watchers for KEY (or all keys if omitted)."""
    vault_path = get_vault_path(profile)
    if key:
        watchers = get_watchers(vault_path, key)
        if not watchers:
            click.echo(f"No watchers for '{key}'.")
        else:
            for w in watchers:
                click.echo(w)
    else:
        all_w = list_all_watchers(vault_path)
        if not all_w:
            click.echo("No watchers registered.")
        else:
            for k, ws in sorted(all_w.items()):
                click.echo(f"{k}: {', '.join(ws)}")


@cmd_watcher.command("clear")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def watcher_clear(key: str, profile: str):
    """Remove all watchers from KEY."""
    vault_path = get_vault_path(profile)
    count = clear_watchers(vault_path, key)
    click.echo(f"Cleared {count} watcher(s) from '{key}'.")
