"""CLI commands for diffing vault vs .env file."""

import click

from envault.cli import _get_password, cli
from envault.diff import diff_vault_vs_file, format_diff
from envault.profiles import get_profile_vault_path


@cli.command("diff")
@click.argument("dotenv_file", default=".env")
@click.option("--profile", default="default", show_default=True, help="Vault profile to use.")
@click.option("--show-unchanged", is_flag=True, default=False, help="Also show unchanged keys.")
@click.option("--hide-values", is_flag=True, default=False, help="Mask secret values in output.")
@click.option("--password", envvar="ENVAULT_PASSWORD", default=None, help="Vault password.")
@click.pass_context
def cmd_diff(ctx: click.Context, dotenv_file: str, profile: str, show_unchanged: bool, hide_values: bool, password: str):
    """Show differences between the vault and a .env file.

    DOTENV_FILE defaults to '.env' in the current directory.
    """
    vault_path = get_profile_vault_path(profile)
    password = _get_password(password)

    try:
        entries = diff_vault_vs_file(
            vault_path=vault_path,
            dotenv_path=dotenv_file,
            password=password,
            show_unchanged=show_unchanged,
        )
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc

    summary = {"added": 0, "removed": 0, "changed": 0, "unchanged": 0}
    for e in entries:
        summary[e.status] += 1

    output = format_diff(entries, hide_values=hide_values)
    click.echo(output)

    if entries:
        parts = []
        if summary["added"]:
            parts.append(click.style(f"+{summary['added']} added", fg="green"))
        if summary["removed"]:
            parts.append(click.style(f"-{summary['removed']} removed", fg="red"))
        if summary["changed"]:
            parts.append(click.style(f"~{summary['changed']} changed", fg="yellow"))
        if summary["unchanged"] and show_unchanged:
            parts.append(f"{summary['unchanged']} unchanged")
        click.echo("\n" + "  ".join(parts))
