"""CLI commands for group management."""

import click

from envault.cli import _get_password
from envault.groups import (
    add_key_to_group,
    create_group,
    delete_group,
    find_groups_for_key,
    get_group_keys,
    list_groups,
    remove_key_from_group,
)
from envault.storage import get_vault_path


@click.group("group")
def cmd_group():
    """Manage secret groups."""


@cmd_group.command("list")
@click.option("--profile", default="default", help="Profile name")
def group_list(profile):
    """List all groups."""
    vault_path = get_vault_path(profile)
    groups = list_groups(vault_path)
    if not groups:
        click.echo("No groups defined.")
    else:
        for g in groups:
            click.echo(g)


@cmd_group.command("create")
@click.argument("name")
@click.option("--profile", default="default", help="Profile name")
def group_create(name, profile):
    """Create a new group."""
    vault_path = get_vault_path(profile)
    try:
        create_group(vault_path, name)
        click.echo(f"Group '{name}' created.")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cmd_group.command("delete")
@click.argument("name")
@click.option("--profile", default="default", help="Profile name")
def group_delete(name, profile):
    """Delete a group."""
    vault_path = get_vault_path(profile)
    try:
        delete_group(vault_path, name)
        click.echo(f"Group '{name}' deleted.")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cmd_group.command("add")
@click.argument("group")
@click.argument("key")
@click.option("--profile", default="default", help="Profile name")
def group_add(group, key, profile):
    """Add a key to a group."""
    vault_path = get_vault_path(profile)
    try:
        add_key_to_group(vault_path, group, key)
        click.echo(f"Key '{key}' added to group '{group}'.")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cmd_group.command("remove")
@click.argument("group")
@click.argument("key")
@click.option("--profile", default="default", help="Profile name")
def group_remove(group, key, profile):
    """Remove a key from a group."""
    vault_path = get_vault_path(profile)
    try:
        remove_key_from_group(vault_path, group, key)
        click.echo(f"Key '{key}' removed from group '{group}'.")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cmd_group.command("show")
@click.argument("name")
@click.option("--profile", default="default", help="Profile name")
def group_show(name, profile):
    """Show keys in a group."""
    vault_path = get_vault_path(profile)
    try:
        keys = get_group_keys(vault_path, name)
        if not keys:
            click.echo(f"Group '{name}' is empty.")
        else:
            for k in keys:
                click.echo(k)
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
