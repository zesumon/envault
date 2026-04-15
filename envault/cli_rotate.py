"""CLI commands for password rotation."""

from __future__ import annotations

import click

from envault.cli import cli, _get_password
from envault.profiles import get_profile_vault_path
from envault.rotate import rotate_password, rotate_dry_run


@cli.command("rotate")
@click.option("--profile", default="default", show_default=True, help="Vault profile.")
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Show which keys would be rotated without writing.",
)
@click.pass_context
def cmd_rotate(ctx: click.Context, profile: str, dry_run: bool) -> None:
    """Re-encrypt all secrets under a new master password."""
    vault_path = get_profile_vault_path(profile)

    old_password = _get_password(prompt="Current master password")

    if dry_run:
        keys = rotate_dry_run(vault_path, old_password)
        if keys is None:
            click.echo("Vault does not exist yet — nothing to rotate.")
            return
        if not keys:
            click.echo("Vault is empty — nothing to rotate.")
            return
        click.echo(f"Would rotate {len(keys)} secret(s):")
        for k in keys:
            click.echo(f"  {k}")
        return

    new_password = _get_password(prompt="New master password")
    confirm = _get_password(prompt="Confirm new master password")

    if new_password != confirm:
        click.echo("Passwords do not match. Aborting.", err=True)
        ctx.exit(1)
        return

    try:
        count = rotate_password(vault_path, old_password, new_password, profile=profile)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Rotation failed: {exc}", err=True)
        ctx.exit(1)
        return

    click.echo(f"Rotated {count} secret(s) to new password.")
