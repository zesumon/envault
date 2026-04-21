"""CLI commands for vault scorecards — run a health score and view history."""

import click
from envault.scorecards import compute_score, get_latest_scorecard
from envault.storage import get_vault_path


@click.group(name="scorecard")
def cmd_scorecard():
    """Run and view vault health scorecards."""


@cmd_scorecard.command(name="run")
@click.option("--profile", default="default", show_default=True, help="Vault profile to score.")
@click.password_option(prompt="Vault password", confirmation_prompt=False, envvar="ENVAULT_PASSWORD")
def scorecard_run(profile: str, password: str):
    """Compute a fresh health score for the vault and save it."""
    vault_path = get_vault_path(profile)
    result = compute_score(vault_path, password)

    score = result["score"]
    color = "green" if score >= 80 else ("yellow" if score >= 50 else "red")

    click.echo(f"\nVault scorecard for profile: {profile}")
    click.echo("-" * 36)
    click.secho(f"  Overall score : {score}/100", fg=color, bold=True)
    click.echo(f"  Total keys    : {result['total_keys']}")
    click.echo(f"  Empty values  : {result['empty_values']}")
    click.echo(f"  Weak values   : {result['weak_values']}")
    click.echo(f"  Expiring soon : {result.get('expiring_soon', 0)}")
    click.echo(f"  No TTL set    : {result.get('no_ttl', 0)}")
    click.echo(f"  Untagged keys : {result.get('untagged', 0)}")
    click.echo(f"  Computed at   : {result['computed_at']}")
    click.echo()


@cmd_scorecard.command(name="show")
@click.option("--profile", default="default", show_default=True, help="Vault profile.")
def scorecard_show(profile: str):
    """Show the most recently computed scorecard without re-running."""
    vault_path = get_vault_path(profile)
    result = get_latest_scorecard(vault_path)

    if result is None:
        click.echo("No scorecard found. Run 'envault scorecard run' first.")
        return

    score = result["score"]
    color = "green" if score >= 80 else ("yellow" if score >= 50 else "red")

    click.echo(f"\nLast scorecard for profile: {profile}")
    click.echo("-" * 36)
    click.secho(f"  Overall score : {score}/100", fg=color, bold=True)
    click.echo(f"  Total keys    : {result['total_keys']}")
    click.echo(f"  Empty values  : {result['empty_values']}")
    click.echo(f"  Weak values   : {result['weak_values']}")
    click.echo(f"  Expiring soon : {result.get('expiring_soon', 0)}")
    click.echo(f"  No TTL set    : {result.get('no_ttl', 0)}")
    click.echo(f"  Untagged keys : {result.get('untagged', 0)}")
    click.echo(f"  Computed at   : {result['computed_at']}")
    click.echo()
