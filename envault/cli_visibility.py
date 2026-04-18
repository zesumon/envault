"""CLI commands for managing key visibility."""
import click
from pathlib import Path

from envault.visibility import (
    set_visibility, get_visibility, remove_visibility,
    list_visibility, VALID_MODES
)


@click.group(name="visibility")
def cmd_visibility():
    """Manage key visibility (public/private/masked)."""


@cmd_visibility.command("set")
@click.argument("key")
@click.argument("mode", type=click.Choice(list(VALID_MODES)))
@click.option("--vault", default=".envault/vault.enc", show_default=True)
def visibility_set(key: str, mode: str, vault: str):
    """Set visibility mode for a key."""
    vault_path = Path(vault)
    set_visibility(vault_path, key, mode)
    click.echo(f"Visibility for '{key}' set to '{mode}'.")


@cmd_visibility.command("get")
@click.argument("key")
@click.option("--vault", default=".envault/vault.enc", show_default=True)
def visibility_get(key: str, vault: str):
    """Get visibility mode for a key."""
    mode = get_visibility(Path(vault), key)
    if mode is None:
        click.echo(f"No visibility set for '{key}' (defaults to public).")
    else:
        click.echo(f"{key}: {mode}")


@cmd_visibility.command("remove")
@click.argument("key")
@click.option("--vault", default=".envault/vault.enc", show_default=True)
def visibility_remove(key: str, vault: str):
    """Remove visibility setting for a key."""
    removed = remove_visibility(Path(vault), key)
    if removed:
        click.echo(f"Visibility setting removed for '{key}'.")
    else:
        click.echo(f"No visibility setting found for '{key}'.")


@cmd_visibility.command("list")
@click.option("--vault", default=".envault/vault.enc", show_default=True)
def visibility_list(vault: str):
    """List all visibility settings."""
    data = list_visibility(Path(vault))
    if not data:
        click.echo("No visibility settings configured.")
        return
    for key, mode in sorted(data.items()):
        click.echo(f"  {key}: {mode}")
