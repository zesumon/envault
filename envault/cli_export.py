"""CLI commands for export, import, and sync operations."""

import click
from pathlib import Path

from envault.cli import _get_password
from envault.export import export_to_file, import_from_file
from envault.storage import load_vault, save_vault, get_vault_path, set_secret
from envault.sync import sync_vault_to_file, sync_file_to_vault


@click.command("export")
@click.argument("output", default=".env", type=click.Path())
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing file.")
def cmd_export(output: str, overwrite: bool) -> None:
    """Export vault secrets to a .env file."""
    password = _get_password(confirm=False)
    vault_path = get_vault_path()
    secrets = load_vault(vault_path, password)
    out_path = Path(output)
    try:
        export_to_file(secrets, out_path, overwrite=overwrite)
        click.echo(f"Exported {len(secrets)} secret(s) to {out_path}")
    except FileExistsError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@click.command("import")
@click.argument("source", default=".env", type=click.Path(exists=True))
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing vault keys.")
def cmd_import(source: str, overwrite: bool) -> None:
    """Import secrets from a .env file into the vault."""
    password = _get_password(confirm=False)
    src_path = Path(source)
    try:
        file_secrets = import_from_file(src_path)
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

    vault_path = get_vault_path()
    vault = load_vault(vault_path, password)
    added = 0
    skipped = 0
    for key, value in file_secrets.items():
        if key in vault and not overwrite:
            skipped += 1
            continue
        set_secret(vault_path, password, key, value)
        added += 1
    click.echo(f"Imported {added} secret(s), skipped {skipped} existing key(s).")


@click.command("sync")
@click.argument("env_file", default=".env", type=click.Path())
@click.option(
    "--direction",
    type=click.Choice(["to-file", "to-vault"]),
    default="to-file",
    show_default=True,
    help="Direction of sync.",
)
@click.option(
    "--conflict",
    type=click.Choice(["vault", "file", "skip"]),
    default="vault",
    show_default=True,
    help="Conflict resolution strategy.",
)
def cmd_sync(env_file: str, direction: str, conflict: str) -> None:
    """Sync secrets between vault and a .env file."""
    password = _get_password(confirm=False)
    path = Path(env_file)
    if direction == "to-file":
        merged = sync_vault_to_file(password, path, conflict=conflict)  # type: ignore[arg-type]
        click.echo(f"Synced {len(merged)} secret(s) from vault → {path}")
    else:
        merged = sync_file_to_vault(password, path, conflict=conflict)  # type: ignore[arg-type]
        click.echo(f"Synced {len(merged)} secret(s) from {path} → vault")
