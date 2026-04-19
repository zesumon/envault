"""CLI commands for category management."""
import click
from pathlib import Path
from envault.categories import (
    set_category, get_category, remove_category,
    list_by_category, list_all_categories, VALID_CATEGORIES
)


@click.group(name="category")
def cmd_category():
    """Manage key categories."""


@cmd_category.command("set")
@click.argument("key")
@click.argument("category")
@click.option("--vault", default=".envault/vault.enc", show_default=True)
def category_set(key, category, vault):
    """Assign a category to a key."""
    try:
        set_category(Path(vault), key, category)
        click.echo(f"Category '{category}' assigned to '{key}'.")
    except (KeyError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cmd_category.command("get")
@click.argument("key")
@click.option("--vault", default=".envault/vault.enc", show_default=True)
def category_get(key, vault):
    """Get the category of a key."""
    cat = get_category(Path(vault), key)
    if cat:
        click.echo(cat)
    else:
        click.echo(f"No category set for '{key}'.")


@cmd_category.command("remove")
@click.argument("key")
@click.option("--vault", default=".envault/vault.enc", show_default=True)
def category_remove(key, vault):
    """Remove category from a key."""
    removed = remove_category(Path(vault), key)
    if removed:
        click.echo(f"Category removed from '{key}'.")
    else:
        click.echo(f"No category set for '{key}'.")


@cmd_category.command("list")
@click.option("--filter", "filter_cat", default=None, help="Filter by category name.")
@click.option("--vault", default=".envault/vault.enc", show_default=True)
def category_list(filter_cat, vault):
    """List keys and their categories."""
    if filter_cat:
        if filter_cat not in VALID_CATEGORIES:
            click.echo(f"Unknown category '{filter_cat}'.", err=True)
            raise SystemExit(1)
        keys = list_by_category(Path(vault), filter_cat)
        if not keys:
            click.echo(f"No keys in category '{filter_cat}'.")
        else:
            for k in keys:
                click.echo(k)
    else:
        data = list_all_categories(Path(vault))
        if not data:
            click.echo("No categories assigned.")
        else:
            for k, v in sorted(data.items()):
                click.echo(f"{k}: {v}")
