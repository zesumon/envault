"""CLI commands for managing envault profiles."""

import click

from envault.profiles import (
    list_profiles,
    create_profile,
    delete_profile,
    DEFAULT_PROFILE,
)
from envault.audit import log_event


@click.group("profile")
def cmd_profile():
    """Manage named secret profiles (e.g. dev, staging, prod)."""


@cmd_profile.command("list")
def cmd_profile_list():
    """List all available profiles."""
    profiles = list_profiles()
    if not profiles:
        click.echo("No profiles found.")
        return
    for name in profiles:
        marker = " (default)" if name == DEFAULT_PROFILE else ""
        click.echo(f"  {name}{marker}")


@cmd_profile.command("create")
@click.argument("name")
def cmd_profile_create(name):
    """Create a new profile NAME."""
    try:
        create_profile(name)
        log_event("profile_create", name)
        click.echo(f"Profile '{name}' created.")
    except ValueError as exc:
        raise click.ClickException(str(exc))


@cmd_profile.command("delete")
@click.argument("name")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt.")
def cmd_profile_delete(name, yes):
    """Delete profile NAME and its stored secrets."""
    if name == DEFAULT_PROFILE and not yes:
        click.echo(
            f"Warning: '{name}' is the default profile.", err=True
        )
    if not yes:
        click.confirm(
            f"Delete profile '{name}' and all its secrets? This cannot be undone.",
            abort=True,
        )
    try:
        delete_profile(name)
        log_event("profile_delete", name)
        click.echo(f"Profile '{name}' deleted.")
    except (ValueError, KeyError) as exc:
        raise click.ClickException(str(exc))
