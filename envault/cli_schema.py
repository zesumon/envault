"""CLI commands for schema validation."""
import click
from pathlib import Path
from envault.storage import get_vault_path, load_vault
from envault import schema as sc


@click.group(name="schema")
def cmd_schema():
    """Manage key schema rules."""


@cmd_schema.command("set")
@click.argument("key")
@click.option("--type", "type_", default="string", show_default=True,
              type=click.Choice(sorted(sc.VALID_TYPES)), help="Expected value type.")
@click.option("--required", is_flag=True, default=False, help="Mark key as required.")
@click.option("--pattern", default=None, help="Optional regex pattern the value must match.")
@click.option("--vault", default=None, help="Vault directory.")
def schema_set(key, type_, required, pattern, vault):
    """Set schema rule for a key."""
    vp = get_vault_path(vault)
    try:
        sc.set_schema(vp, key, type_, required=required, pattern=pattern)
        click.echo(f"Schema set for '{key}' (type={type_}, required={required}).")
    except (ValueError, Exception) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cmd_schema.command("remove")
@click.argument("key")
@click.option("--vault", default=None)
def schema_remove(key, vault):
    """Remove schema rule for a key."""
    vp = get_vault_path(vault)
    if sc.remove_schema(vp, key):
        click.echo(f"Schema rule removed for '{key}'.")
    else:
        click.echo(f"No schema rule found for '{key}'.")


@cmd_schema.command("list")
@click.option("--vault", default=None)
def schema_list(vault):
    """List all schema rules."""
    vp = get_vault_path(vault)
    rules = sc.list_schema(vp)
    if not rules:
        click.echo("No schema rules defined.")
        return
    for key, rule in sorted(rules.items()):
        req = " [required]" if rule.get("required") else ""
        pat = f" pattern={rule['pattern']}" if "pattern" in rule else ""
        click.echo(f"{key}: type={rule['type']}{req}{pat}")


@cmd_schema.command("check")
@click.option("--vault", default=None)
@click.option("--password", default=None, envvar="ENVAULT_PASSWORD")
def schema_check(vault, password):
    """Validate all vault values against schema rules."""
    from envault.cli import _get_password
    vp = get_vault_path(vault)
    pw = password or _get_password()
    secrets = load_vault(vp, pw)
    issues = []
    for key, value in secrets.items():
        errs = sc.validate_value(vp, key, value)
        for e in errs:
            issues.append(f"  {key}: {e}")
    missing = sc.validate_required(vp, set(secrets.keys()))
    for k in missing:
        issues.append(f"  {k}: required key is missing")
    if issues:
        click.echo("Schema validation failed:")
        for i in issues:
            click.echo(i)
        raise SystemExit(1)
    click.echo("All values pass schema validation.")
