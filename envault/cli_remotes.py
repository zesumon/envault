"""CLI commands for managing named remotes."""

import click
from pathlib import Path

from envault.remotes import (
    list_remotes,
    add_remote,
    update_remote,
    remove_remote,
    get_remote,
)


@click.group("remote")
def cmd_remote():
    """Manage named remote endpoints."""


@cmd_remote.command("list")
@click.pass_context
def remote_list(ctx):
    """List all registered remotes."""
    vault_dir = Path(ctx.obj["vault_dir"])
    remotes = list_remotes(vault_dir)
    if not remotes:
        click.echo("No remotes configured.")
        return
    for r in remotes:
        click.echo(f"  {r['name']}  {r['url']}")


@cmd_remote.command("add")
@click.argument("name")
@click.argument("url")
@click.pass_context
def remote_add(ctx, name: str, url: str):
    """Add a new named remote."""
    vault_dir = Path(ctx.obj["vault_dir"])
    try:
        add_remote(vault_dir, name, url)
        click.echo(f"Remote '{name}' added.")
    except (ValueError, KeyError) as exc:
        raise click.ClickException(str(exc))


@cmd_remote.command("update")
@click.argument("name")
@click.argument("url")
@click.pass_context
def remote_update(ctx, name: str, url: str):
    """Update the URL of an existing remote."""
    vault_dir = Path(ctx.obj["vault_dir"])
    try:
        update_remote(vault_dir, name, url)
        click.echo(f"Remote '{name}' updated.")
    except (ValueError, KeyError) as exc:
        raise click.ClickException(str(exc))


@cmd_remote.command("remove")
@click.argument("name")
@click.pass_context
def remote_remove(ctx, name: str):
    """Remove a named remote."""
    vault_dir = Path(ctx.obj["vault_dir"])
    try:
        remove_remote(vault_dir, name)
        click.echo(f"Remote '{name}' removed.")
    except KeyError as exc:
        raise click.ClickException(str(exc))


@cmd_remote.command("show")
@click.argument("name")
@click.pass_context
def remote_show(ctx, name: str):
    """Show the URL for a named remote."""
    vault_dir = Path(ctx.obj["vault_dir"])
    url = get_remote(vault_dir, name)
    if url is None:
        raise click.ClickException(f"Remote '{name}' not found.")
    click.echo(url)
