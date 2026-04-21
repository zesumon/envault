"""CLI commands for vault scorecards."""

import click

from envault.cli import cli, _get_password
from envault.storage import get_vault_path
from envault.scorecards import compute_score, get_latest_scorecard


@cli.group("scorecard")
def cmd_scorecard() -> None:
    """Vault health scorecard commands."""


@cmd_scorecard.command("run")
@click.option("--profile", default="default", show_default=True, help="Profile name.")
@click.option("--password", envvar="ENVAULT_PASSWORD", default=None, help="Vault password.")
def scorecard_run(profile: str, password: str | None) -> None:
    """Compute and display the vault health score."""
    vault_path = get_vault_path(profile)
    pw = _get_password(password)
    report = compute_score(vault_path, pw)

    score = report["score"]
    colour = "green" if score >= 80 else "yellow" if score >= 50 else "red"
    click.echo(f"Health score: {click.style(str(score), fg=colour, bold=True)}/100")
    click.echo(f"Total keys  : {report['total_keys']}")

    bd = report["breakdown"]
    click.echo(f"  Lint penalty      : -{bd['lint_penalty']}")
    click.echo(f"  Expired penalty   : -{bd['expired_penalty']} ({bd['expired_keys']} keys)")
    click.echo(f"  Checksum penalty  : -{bd['checksum_penalty']} ({bd['checksum_failures']} failures)")

    if report["issues"]:
        click.echo("\nIssues:")
        for issue in report["issues"]:
            click.echo(f"  - {issue}")
    else:
        click.echo("\nNo issues found.")


@cmd_scorecard.command("show")
@click.option("--profile", default="default", show_default=True, help="Profile name.")
def scorecard_show(profile: str) -> None:
    """Show the most recently computed scorecard (without re-running)."""
    vault_path = get_vault_path(profile)
    report = get_latest_scorecard(vault_path)
    if report is None:
        click.echo("No scorecard found. Run 'envault scorecard run' first.")
        return

    score = report["score"]
    colour = "green" if score >= 80 else "yellow" if score >= 50 else "red"
    click.echo(f"Cached health score: {click.style(str(score), fg=colour, bold=True)}/100")
    click.echo(f"Total keys: {report['total_keys']}")
    if report["issues"]:
        click.echo("Issues:")
        for issue in report["issues"]:
            click.echo(f"  - {issue}")
