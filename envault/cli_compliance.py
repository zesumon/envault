"""CLI commands for compliance checking."""

from __future__ import annotations

import click

from envault.cli import _get_password
from envault.storage import get_vault_path
from envault.compliance import run_compliance


@click.group("compliance")
def cmd_compliance():
    """Compliance policy checks for vault secrets."""


@cmd_compliance.command("check")
@click.option("--profile", default="default", show_default=True, help="Vault profile to check.")
@click.option("--strict", is_flag=True, default=False, help="Exit non-zero on warnings too.")
def compliance_check(profile: str, strict: bool):
    """Run compliance checks and report issues."""
    password = _get_password()
    vault_path = get_vault_path(profile)

    if not vault_path.exists():
        click.echo("No vault found for this profile.")
        raise SystemExit(1)

    report = run_compliance(vault_path, password)

    if not report.issues:
        click.secho("✓ All compliance checks passed.", fg="green")
        return

    for issue in report.errors:
        click.secho(f"  [ERROR]   {issue.key}: {issue.rule}", fg="red")
    for issue in report.warnings:
        click.secho(f"  [WARNING] {issue.key}: {issue.rule}", fg="yellow")

    click.echo(f"\n{len(report.errors)} error(s), {len(report.warnings)} warning(s).")

    if not report.passed or (strict and report.warnings):
        raise SystemExit(1)


@cmd_compliance.command("summary")
@click.option("--profile", default="default", show_default=True)
def compliance_summary(profile: str):
    """Print a one-line compliance summary."""
    password = _get_password()
    vault_path = get_vault_path(profile)

    if not vault_path.exists():
        click.echo("No vault found.")
        raise SystemExit(1)

    report = run_compliance(vault_path, password)
    status = "PASS" if report.passed else "FAIL"
    color = "green" if report.passed else "red"
    click.secho(
        f"Compliance: {status} | errors={len(report.errors)} warnings={len(report.warnings)}",
        fg=color,
    )
