"""CLI commands for managing key labels."""
import click
from envault.storage import get_vault_path
from envault.labels import set_label, get_label, remove_label, list_labels


@click.group("label")
def cmd_label():
    """Attach human-readable labels to secret keys."""


@cmd_label.command("set")
@click.argument("key")
@click.argument("label")
@click.option("--profile", default="default", show_default=True)
def label_set(key: str, label: str, profile: str):
    """Set a label for KEY."""
    vp = get_vault_path(profile)
    set_label(vp, key, label)
    click.echo(f"Label set: {key} → {label}")


@cmd_label.command("get")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def label_get(key: str, profile: str):
    """Get the label for KEY."""
    vp = get_vault_path(profile)
    label = get_label(vp, key)
    if label is None:
        click.echo(f"No label set for '{key}'.")
    else:
        click.echo(label)


@cmd_label.command("remove")
@click.argument("key")
@click.option("--profile", default="default", show_default=True)
def label_remove(key: str, profile: str):
    """Remove the label for KEY."""
    vp = get_vault_path(profile)
    removed = remove_label(vp, key)
    if removed:
        click.echo(f"Label removed for '{key}'.")
    else:
        click.echo(f"No label found for '{key}'.")


@cmd_label.command("list")
@click.option("--profile", default="default", show_default=True)
def label_list(profile: str):
    """List all key labels."""
    vp = get_vault_path(profile)
    data = list_labels(vp)
    if not data:
        click.echo("No labels defined.")
        return
    width = max(len(k) for k in data)
    for key, label in data.items():
        click.echo(f"  {key:<{width}}  {label}")
