"""CLI commands for managing secret TTLs."""

import click
from pathlib import Path
from envault.cli import cli, _get_password
from envault.storage import get_vault_path, load_vault
from envault.ttl import set_ttl, get_ttl, clear_ttl, purge_expired, is_expired


@cli.group("ttl")
def cmd_ttl():
    """Manage expiry (TTL) for secrets."""
    pass


@cmd_ttl.command("set")
@click.argument("key")
@click.argument("seconds", type=int)
@click.option("--profile", default="default", show_default=True)
def ttl_set(key: str, seconds: int, profile: str):
    """Set TTL for KEY to SECONDS seconds from now."""
    vault_path = get_vault_path(profile)
    password = _get_password()
    vault = load_vault(vault_path, password)
    if key not in vault:
        raise click.ClickException(f"Key '{key}' not found in vault.")
    expires_at = set_ttl(vault_path, key, seconds)
    click.echo(f"TTL set for '{key}': expires at {expires_at}")


@cmd_ttl.command("get")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def ttl_get(key: str, profile: str):
    """Show TTL expiry for KEY."""
    vault_path = get_vault_path(profile)
    expiry = get_ttl(vault_path, key)
    if expiry is None:
        click.echo(f"No TTL set for '{key}'.")
    else:
        expired = is_expired(vault_path, key)
        status = " (EXPIRED)" if expired else ""
        click.echo(f"'{key}' expires at: {expiry}{status}")


@cmd_ttl.command("clear")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def ttl_clear(key: str, profile: str):
    """Remove TTL for KEY."""
    vault_path = get_vault_path(profile)
    removed = clear_ttl(vault_path, key)
    if removed:
        click.echo(f"TTL cleared for '{key}'.")
    else:
        click.echo(f"No TTL was set for '{key}'.")


@cmd_ttl.command("purge")
@click.option("--profile", default="default", show_default=True)
def ttl_purge(profile: str):
    """Delete all expired secrets from the vault."""
    vault_path = get_vault_path(profile)
    password = _get_password()
    purged = purge_expired(vault_path, password)
    if purged:
        for key in purged:
            click.echo(f"Purged expired key: {key}")
        click.echo(f"{len(purged)} key(s) purged.")
    else:
        click.echo("No expired keys found.")
