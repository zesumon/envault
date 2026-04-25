"""CLI commands for viewing and managing the vault changelog."""

import click
from envault.changelog import add_entry, get_changelog, clear_changelog, _get_changelog_path
from envault.storage import get_vault_path


@click.group(name="changelog")
def cmd_changelog():
    """View and manage the vault changelog."""
    pass


@cmd_changelog.command(name="list")
@click.option("--profile", default="default", show_default=True, help="Vault profile to use.")
@click.option("--tail", default=0, type=int, help="Show only the last N entries (0 = all).")
@click.option("--key", default=None, help="Filter entries by key name.")
@click.option("--action", default=None, help="Filter entries by action type.")
def changelog_list(profile, tail, key, action):
    """List changelog entries for the vault."""
    vault_path = get_vault_path(profile)
    entries = get_changelog(vault_path)

    if key:
        entries = [e for e in entries if e.get("key") == key]
    if action:
        entries = [e for e in entries if e.get("action") == action]
    if tail and tail > 0:
        entries = entries[-tail:]

    if not entries:
        click.echo("No changelog entries found.")
        return

    for entry in entries:
        ts = entry.get("timestamp", "?")
        act = entry.get("action", "?")
        k = entry.get("key", "")
        note = entry.get("note", "")
        parts = [f"[{ts}]", act.upper()]
        if k:
            parts.append(k)
        if note:
            parts.append(f"— {note}")
        click.echo(" ".join(parts))


@cmd_changelog.command(name="add")
@click.argument("action")
@click.argument("key")
@click.option("--profile", default="default", show_default=True, help="Vault profile to use.")
@click.option("--note", default="", help="Optional note to attach to the entry.")
def changelog_add(action, key, profile, note):
    """Manually add a changelog entry."""
    vault_path = get_vault_path(profile)
    add_entry(vault_path, action=action, key=key, note=note)
    click.echo(f"Changelog entry added: {action.upper()} {key}")


@cmd_changelog.command(name="clear")
@click.option("--profile", default="default", show_default=True, help="Vault profile to use.")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt.")
def changelog_clear(profile, yes):
    """Clear all changelog entries for the vault."""
    vault_path = get_vault_path(profile)
    if not yes:
        click.confirm("Are you sure you want to clear the changelog?", abort=True)
    clear_changelog(vault_path)
    click.echo("Changelog cleared.")


@cmd_changelog.command(name="show")
@click.argument("key")
@click.option("--profile", default="default", show_default=True, help="Vault profile to use.")
def changelog_show(key, profile):
    """Show changelog entries for a specific key."""
    vault_path = get_vault_path(profile)
    entries = get_changelog(vault_path)
    key_entries = [e for e in entries if e.get("key") == key]

    if not key_entries:
        click.echo(f"No changelog entries found for key: {key}")
        return

    click.echo(f"Changelog for '{key}':")
    for entry in key_entries:
        ts = entry.get("timestamp", "?")
        act = entry.get("action", "?")
        note = entry.get("note", "")
        line = f"  [{ts}] {act.upper()}"
        if note:
            line += f" — {note}"
        click.echo(line)
