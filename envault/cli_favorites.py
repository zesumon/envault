"""CLI commands for managing favorite keys."""

from __future__ import annotations

import click

from envault.cli import _get_password
from envault.favorites import (
    add_favorite,
    clear_favorites,
    is_favorite,
    list_favorites,
    remove_favorite,
)
from envault.storage import get_vault_path


@click.group("favorite")
def cmd_favorite() -> None:
    """Manage favorite keys."""


@cmd_favorite.command("list")
@click.option("--profile", default="default", show_default=True)
def favorite_list(profile: str) -> None:
    """List all favorite keys."""
    vault_path = get_vault_path(profile)
    favs = list_favorites(vault_path)
    if not favs:
        click.echo("No favorites set.")
        return
    for key in favs:
        click.echo(key)


@cmd_favorite.command("add")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def favorite_add(key: str, profile: str) -> None:
    """Add KEY to favorites."""
    vault_path = get_vault_path(profile)
    password = _get_password()
    try:
        add_favorite(vault_path, key, password)
        click.echo(f"Added '{key}' to favorites.")
    except KeyError as exc:
        raise click.ClickException(str(exc))


@cmd_favorite.command("remove")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def favorite_remove(key: str, profile: str) -> None:
    """Remove KEY from favorites."""
    vault_path = get_vault_path(profile)
    removed = remove_favorite(vault_path, key)
    if removed:
        click.echo(f"Removed '{key}' from favorites.")
    else:
        click.echo(f"'{key}' was not in favorites.")


@cmd_favorite.command("check")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def favorite_check(key: str, profile: str) -> None:
    """Check whether KEY is a favorite."""
    vault_path = get_vault_path(profile)
    if is_favorite(vault_path, key):
        click.echo(f"'{key}' is a favorite.")
    else:
        click.echo(f"'{key}' is NOT a favorite.")


@cmd_favorite.command("clear")
@click.option("--profile", default="default", show_default=True)
@click.confirmation_option(prompt="Clear all favorites?")
def favorite_clear(profile: str) -> None:
    """Remove all favorites."""
    vault_path = get_vault_path(profile)
    count = clear_favorites(vault_path)
    click.echo(f"Cleared {count} favorite(s).")
