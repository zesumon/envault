"""CLI commands for template management."""

import click
from pathlib import Path

from envault.storage import get_vault_path, load_vault
from envault.templates import (
    list_templates,
    save_template,
    delete_template,
    get_template_keys,
    check_missing_keys,
)


@click.group("template")
def cmd_template():
    """Manage key templates (scaffolds for required keys)."""


@cmd_template.command("list")
@click.option("--vault-dir", default=None, hidden=True)
def template_list(vault_dir):
    """List all saved templates."""
    vdir = Path(vault_dir) if vault_dir else get_vault_path().parent
    names = list_templates(vdir)
    if not names:
        click.echo("No templates defined.")
        return
    for name in names:
        keys = get_template_keys(vdir, name)
        click.echo(f"{name}: {', '.join(keys)}")


@cmd_template.command("save")
@click.argument("name")
@click.argument("keys", nargs=-1, required=True)
@click.option("--vault-dir", default=None, hidden=True)
def template_save(name, keys, vault_dir):
    """Save a template with the given KEYS."""
    vdir = Path(vault_dir) if vault_dir else get_vault_path().parent
    try:
        save_template(vdir, name, list(keys))
        click.echo(f"Template '{name}' saved with {len(set(keys))} key(s).")
    except ValueError as e:
        raise click.ClickException(str(e))


@cmd_template.command("delete")
@click.argument("name")
@click.option("--vault-dir", default=None, hidden=True)
def template_delete(name, vault_dir):
    """Delete a template by NAME."""
    vdir = Path(vault_dir) if vault_dir else get_vault_path().parent
    try:
        delete_template(vdir, name)
        click.echo(f"Template '{name}' deleted.")
    except KeyError as e:
        raise click.ClickException(str(e))


@cmd_template.command("check")
@click.argument("name")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--vault-dir", default=None, hidden=True)
def template_check(name, password, vault_dir):
    """Check which template keys are missing from the vault."""
    vdir = Path(vault_dir) if vault_dir else get_vault_path().parent
    vault_file = vdir / "vault.enc"
    try:
        vault = load_vault(vault_file, password)
        present = list(vault.keys())
        missing = check_missing_keys(vdir, name, present)
        if not missing:
            click.echo(f"All keys for template '{name}' are present.")
        else:
            click.echo(f"Missing keys for template '{name}':")
            for k in missing:
                click.echo(f"  - {k}")
    except KeyError as e:
        raise click.ClickException(str(e))
