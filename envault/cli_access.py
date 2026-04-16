"""CLI commands for access control."""
import click
from pathlib import Path
from envault.storage import get_vault_path
from envault import access as acc


@click.group("access")
def cmd_access():
    """Manage key-level access control per profile."""


@cmd_access.command("set")
@click.argument("profile")
@click.argument("key")
@click.option("--read/--no-read", default=True, show_default=True)
@click.option("--write/--no-write", default=True, show_default=True)
@click.option("--vault-dir", default=None, hidden=True)
def access_set(profile, key, read, write, vault_dir):
    """Set access modes for PROFILE on KEY."""
    vault_path = get_vault_path(vault_dir)
    modes = []
    if read:
        modes.append("read")
    if write:
        modes.append("write")
    if not modes:
        raise click.UsageError("At least one of --read or --write must be enabled.")
    acc.set_access(vault_path, profile, key, modes)
    click.echo(f"Access for '{profile}' on '{key}': {modes}")


@cmd_access.command("remove")
@click.argument("profile")
@click.argument("key")
@click.option("--vault-dir", default=None, hidden=True)
def access_remove(profile, key, vault_dir):
    """Remove access restriction for PROFILE on KEY."""
    vault_path = get_vault_path(vault_dir)
    acc.remove_access(vault_path, profile, key)
    click.echo(f"Access restriction removed for '{profile}' on '{key}'.")


@cmd_access.command("list")
@click.argument("profile")
@click.option("--vault-dir", default=None, hidden=True)
def access_list(profile, vault_dir):
    """List all access rules for PROFILE."""
    vault_path = get_vault_path(vault_dir)
    rules = acc.list_access(vault_path, profile)
    if not rules:
        click.echo(f"No access rules for profile '{profile}'.")
        return
    for key, modes in sorted(rules.items()):
        click.echo(f"  {key}: {', '.join(modes)}")


@cmd_access.command("check")
@click.argument("profile")
@click.argument("key")
@click.option("--vault-dir", default=None, hidden=True)
def access_check(profile, key, vault_dir):
    """Check effective access for PROFILE on KEY."""
    vault_path = get_vault_path(vault_dir)
    r = acc.can_read(vault_path, profile, key)
    w = acc.can_write(vault_path, profile, key)
    click.echo(f"read={r}  write={w}")
