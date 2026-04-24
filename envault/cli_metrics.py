"""CLI commands for vault metrics."""

from __future__ import annotations

import click

from envault.cli import cli, _get_password
from envault.storage import get_vault_path
from envault.metrics import compute_metrics, format_metrics


@cli.group("metrics")
def cmd_metrics() -> None:
    """Show vault usage metrics."""


@cmd_metrics.command("show")
@click.option("--profile", default="default", show_default=True, help="Vault profile.")
@click.option("--password", envvar="ENVAULT_PASSWORD", default=None, help="Vault password.")
def metrics_show(profile: str, password: str | None) -> None:
    """Print a summary of vault metrics."""
    vault_path = get_vault_path(profile)
    pw = _get_password(password)
    try:
        m = compute_metrics(vault_path, pw)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc
    click.echo(format_metrics(m))


@cmd_metrics.command("keys")
@click.option("--profile", default="default", show_default=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", default=None)
def metrics_keys(profile: str, password: str | None) -> None:
    """Print only the key count."""
    vault_path = get_vault_path(profile)
    pw = _get_password(password)
    try:
        m = compute_metrics(vault_path, pw)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc
    click.echo(str(m.total_keys))


@cmd_metrics.command("actions")
@click.option("--profile", default="default", show_default=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", default=None)
def metrics_actions(profile: str, password: str | None) -> None:
    """Print a breakdown of audit actions."""
    vault_path = get_vault_path(profile)
    pw = _get_password(password)
    try:
        m = compute_metrics(vault_path, pw)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc
    if not m.action_counts:
        click.echo("No audit events recorded.")
        return
    for action, count in sorted(m.action_counts.items()):
        click.echo(f"{action:<20} {count}")
