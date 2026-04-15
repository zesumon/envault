"""CLI commands for creating and opening share bundles."""

import click
from envault.cli import _get_password
from envault.profiles import get_profile_vault_path
from envault.share import create_share, open_share, list_shares, delete_share


@click.group("share")
def cmd_share():
    """Share secrets via encrypted, time-limited bundles."""


@cmd_share.command("create")
@click.argument("keys", nargs=-1, required=True)
@click.option("--profile", default="default", show_default=True)
@click.option("--ttl", default=3600, show_default=True, help="TTL in seconds")
@click.option("--share-password", prompt=True, hide_input=True, confirmation_prompt=True)
def share_create(keys, profile, ttl, share_password):
    """Create a share bundle for one or more keys."""
    vault_path = get_profile_vault_path(profile)
    password = _get_password()
    try:
        slug = create_share(vault_path, password, share_password, list(keys), ttl_seconds=ttl)
        click.echo(f"Share created: {slug}")
    except KeyError as exc:
        raise click.ClickException(str(exc))


@cmd_share.command("open")
@click.argument("share_name")
@click.option("--profile", default="default", show_default=True)
@click.option("--share-password", prompt=True, hide_input=True)
def share_open(share_name, profile, share_password):
    """Decrypt and display secrets from a share bundle."""
    vault_path = get_profile_vault_path(profile)
    try:
        secrets = open_share(vault_path, share_name, share_password)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))
    except ValueError as exc:
        raise click.ClickException(str(exc))

    for key, value in sorted(secrets.items()):
        click.echo(f"{key}={value}")


@cmd_share.command("list")
@click.option("--profile", default="default", show_default=True)
def share_list(profile):
    """List available share bundles."""
    vault_path = get_profile_vault_path(profile)
    shares = list_shares(vault_path)
    if not shares:
        click.echo("No shares found.")
    else:
        for name in shares:
            click.echo(name)


@cmd_share.command("delete")
@click.argument("share_name")
@click.option("--profile", default="default", show_default=True)
def share_delete(share_name, profile):
    """Delete a share bundle."""
    vault_path = get_profile_vault_path(profile)
    try:
        delete_share(vault_path, share_name)
        click.echo(f"Deleted share: {share_name}")
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))
