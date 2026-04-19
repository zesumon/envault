"""CLI commands for key mention/reference tracking."""
import click
from pathlib import Path

from envault.mentions import add_mention, remove_mention, get_mentions, list_all_mentions, clear_mentions
from envault.storage import get_vault_path


@click.group("mention")
def cmd_mention():
    """Track which keys reference other keys."""


@cmd_mention.command("add")
@click.argument("key")
@click.argument("mentioned_by")
@click.option("--vault", default=None)
def mention_add(key, mentioned_by, vault):
    """Record that MENTIONED_BY references KEY."""
    vp = Path(vault) if vault else get_vault_path()
    try:
        add_mention(vp, key, mentioned_by)
        click.echo(f"Recorded: '{mentioned_by}' mentions '{key}'.")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@cmd_mention.command("remove")
@click.argument("key")
@click.argument("mentioned_by")
@click.option("--vault", default=None)
def mention_remove(key, mentioned_by, vault):
    """Remove a mention record."""
    vp = Path(vault) if vault else get_vault_path()
    removed = remove_mention(vp, key, mentioned_by)
    if removed:
        click.echo(f"Removed mention of '{key}' by '{mentioned_by}'.")
    else:
        click.echo(f"No such mention found.", err=True)


@cmd_mention.command("list")
@click.argument("key", required=False)
@click.option("--vault", default=None)
def mention_list(key, vault):
    """List mentions for KEY, or all keys if omitted."""
    vp = Path(vault) if vault else get_vault_path()
    if key:
        refs = get_mentions(vp, key)
        if refs:
            for r in refs:
                click.echo(r)
        else:
            click.echo(f"No mentions recorded for '{key}'.")
    else:
        data = list_all_mentions(vp)
        if not data:
            click.echo("No mentions recorded.")
        else:
            for k, refs in sorted(data.items()):
                click.echo(f"{k}: {', '.join(refs)}")


@cmd_mention.command("clear")
@click.argument("key")
@click.option("--vault", default=None)
def mention_clear(key, vault):
    """Clear all mention records for KEY."""
    vp = Path(vault) if vault else get_vault_path()
    n = clear_mentions(vp, key)
    click.echo(f"Cleared {n} mention(s) for '{key}'.")
