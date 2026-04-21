"""CLI commands for managing bookmarks."""

import click
from pathlib import Path

from .bookmarks import add_bookmark, remove_bookmark, list_bookmarks, resolve_bookmark
from .cli import _get_password
from .storage import get_vault_path, get_secret


@click.group("bookmark")
def cmd_bookmark():
    """Manage key bookmarks."""


@cmd_bookmark.command("add")
@click.argument("name")
@click.argument("key")
@click.option("--note", default="", help="Optional note for this bookmark.")
@click.option("--profile", default="default")
def bookmark_add(name, key, note, profile):
    """Bookmark KEY under NAME."""
    vault_path = get_vault_path(profile)
    try:
        add_bookmark(vault_path, name, key, note)
        click.echo(f"Bookmarked '{key}' as '{name}'.")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cmd_bookmark.command("remove")
@click.argument("name")
@click.option("--profile", default="default")
def bookmark_remove(name, profile):
    """Remove bookmark NAME."""
    vault_path = get_vault_path(profile)
    try:
        remove_bookmark(vault_path, name)
        click.echo(f"Removed bookmark '{name}'.")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cmd_bookmark.command("list")
@click.option("--profile", default="default")
def bookmark_list(profile):
    """List all bookmarks."""
    vault_path = get_vault_path(profile)
    entries = list_bookmarks(vault_path)
    if not entries:
        click.echo("No bookmarks saved.")
        return
    for e in entries:
        note_part = f"  # {e['note']}" if e["note"] else ""
        click.echo(f"{e['name']:20s} -> {e['key']}{note_part}")


@cmd_bookmark.command("go")
@click.argument("name")
@click.option("--profile", default="default")
def bookmark_go(name, profile):
    """Resolve bookmark NAME and show its secret value."""
    vault_path = get_vault_path(profile)
    key = resolve_bookmark(vault_path, name)
    if key is None:
        click.echo(f"Bookmark '{name}' not found.", err=True)
        raise SystemExit(1)
    password = _get_password()
    value = get_secret(vault_path, password, key)
    if value is None:
        click.echo(f"Key '{key}' not found in vault.", err=True)
        raise SystemExit(1)
    click.echo(f"{key}={value}")
