"""Main CLI entry point for envault."""

import click
from getpass import getpass
from typing import Optional

from envault.storage import get_vault_path, load_vault, save_vault, set_secret, get_secret, delete_secret, list_keys
from envault.audit import log_event
from envault.cli_export import cmd_export, cmd_import, cmd_sync
from envault.cli_audit import cmd_audit, cmd_audit_clear
from envault.cli_profiles import cmd_profile
from envault.profiles import get_profile_vault_path, list_profiles


def _get_password(prompt: str = "Vault password") -> str:
    return getpass(f"{prompt}: ")


@click.group()
def cli():
    """envault — secure .env management."""


@cli.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--profile", default="default", help="Profile to use.")
def cmd_set(key, value, profile):
    """Set a secret KEY to VALUE."""
    password = _get_password()
    vault_path = get_profile_vault_path(profile)
    vault = load_vault(vault_path, password)
    set_secret(vault, key, value)
    save_vault(vault_path, vault, password)
    log_event("set", key)
    click.echo(f"Set '{key}' in profile '{profile}'.")


@cli.command("get")
@click.argument("key")
@click.option("--profile", default="default", help="Profile to use.")
def cmd_get(key, profile):
    """Get the value of secret KEY."""
    password = _get_password()
    vault_path = get_profile_vault_path(profile)
    vault = load_vault(vault_path, password)
    value = get_secret(vault, key)
    if value is None:
        raise click.ClickException(f"Key '{key}' not found in profile '{profile}'.")
    click.echo(value)


@cli.command("delete")
@click.argument("key")
@click.option("--profile", default="default", help="Profile to use.")
def cmd_delete(key, profile):
    """Delete secret KEY."""
    password = _get_password()
    vault_path = get_profile_vault_path(profile)
    vault = load_vault(vault_path, password)
    delete_secret(vault, key)
    save_vault(vault_path, vault, password)
    log_event("delete", key)
    click.echo(f"Deleted '{key}' from profile '{profile}'.")


@cli.command("list")
@click.option("--profile", default="default", help="Profile to use.")
def cmd_list(profile):
    """List all secret keys."""
    password = _get_password()
    vault_path = get_profile_vault_path(profile)
    vault = load_vault(vault_path, password)
    keys = list_keys(vault)
    if not keys:
        click.echo(f"No secrets in profile '{profile}'.")
    for k in keys:
        click.echo(f"  {k}")


cli.add_command(cmd_export, "export")
cli.add_command(cmd_import, "import")
cli.add_command(cmd_sync, "sync")
cli.add_command(cmd_audit, "audit")
cli.add_command(cmd_audit_clear, "audit-clear")
cli.add_command(cmd_profile, "profile")


if __name__ == "__main__":
    cli()
