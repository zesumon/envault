"""CLI commands for key expiry management."""
import click
from datetime import datetime, timezone
from pathlib import Path

from envault.cli import _get_password
from envault.storage import get_vault_path
from envault.expiry import set_expiry, get_expiry, remove_expiry, list_expiry, list_expired, purge_expired


@click.group("expiry")
def cmd_expiry():
    """Manage key expiration dates."""


@cmd_expiry.command("set")
@click.argument("key")
@click.argument("expires_at")  # ISO format: 2025-12-31T00:00:00
@click.option("--profile", default="default")
def expiry_set(key, expires_at, profile):
    """Set expiration date for KEY (ISO datetime)."""
    vault_path = get_vault_path(profile)
    try:
        dt = datetime.fromisoformat(expires_at).replace(tzinfo=timezone.utc)
    except ValueError:
        raise click.ClickException(f"Invalid datetime format: {expires_at}")
    iso = set_expiry(vault_path, key, dt)
    click.echo(f"Expiry set for '{key}': {iso}")


@cmd_expiry.command("get")
@click.argument("key")
@click.option("--profile", default="default")
def expiry_get(key, profile):
    """Get expiration date for KEY."""
    vault_path = get_vault_path(profile)
    val = get_expiry(vault_path, key)
    if val is None:
        click.echo(f"No expiry set for '{key}'.")
    else:
        click.echo(val)


@cmd_expiry.command("remove")
@click.argument("key")
@click.option("--profile", default="default")
def expiry_remove(key, profile):
    """Remove expiration date for KEY."""
    vault_path = get_vault_path(profile)
    if remove_expiry(vault_path, key):
        click.echo(f"Expiry removed for '{key}'.")
    else:
        click.echo(f"No expiry found for '{key}'.")


@cmd_expiry.command("list")
@click.option("--profile", default="default")
@click.option("--expired-only", is_flag=True)
def expiry_list(profile, expired_only):
    """List keys with expiration dates."""
    vault_path = get_vault_path(profile)
    if expired_only:
        keys = list_expired(vault_path)
        if not keys:
            click.echo("No expired keys.")
        for k in keys:
            click.echo(f"EXPIRED  {k}")
    else:
        items = list_expiry(vault_path)
        if not items:
            click.echo("No expiry entries.")
        now = datetime.now(timezone.utc)
        for k, v in items:
            dt = datetime.fromisoformat(v)
            status = "EXPIRED" if dt <= now else "ok     "
            click.echo(f"{status}  {k}  {v}")


@cmd_expiry.command("purge")
@click.option("--profile", default="default")
def expiry_purge(profile):
    """Delete all expired keys from the vault."""
    vault_path = get_vault_path(profile)
    password = _get_password()
    removed = purge_expired(vault_path, password)
    if not removed:
        click.echo("Nothing to purge.")
    else:
        for k in removed:
            click.echo(f"Purged: {k}")
        click.echo(f"{len(removed)} key(s) purged.")
