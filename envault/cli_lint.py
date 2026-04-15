"""CLI commands for vault linting."""
from __future__ import annotations

import click

from envault.cli import cli, _get_password
from envault.profiles import get_profile_vault_path
from envault.lint import lint_vault


@cli.command("lint")
@click.option("--profile", default="default", show_default=True, help="Profile to lint")
@click.option("--password", envvar="ENVAULT_PASSWORD", default=None, help="Vault password")
@click.option("--strict", is_flag=True, default=False, help="Exit non-zero on warnings too")
def cmd_lint(profile: str, password: str | None, strict: bool) -> None:
    """Lint secrets in the vault for common issues."""
    vault_path = get_profile_vault_path(profile)
    if password is None:
        password = _get_password(confirm=False)

    result = lint_vault(vault_path, password)

    if not result.issues:
        click.secho("✔ No issues found.", fg="green")
        return

    for issue in result.issues:
        color = "red" if issue.severity == "error" else "yellow"
        prefix = "ERROR  " if issue.severity == "error" else "WARN   "
        click.secho(f"{prefix} {issue.message}", fg=color)

    total = len(result.issues)
    errors = len(result.errors)
    warnings = len(result.warnings)
    click.echo(f"\n{total} issue(s): {errors} error(s), {warnings} warning(s)")

    if not result.ok or (strict and result.warnings):
        raise SystemExit(1)
