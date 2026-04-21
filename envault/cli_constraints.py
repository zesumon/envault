"""CLI commands for managing key constraints."""

import click
from pathlib import Path

from envault.storage import get_vault_path
from envault.constraints import (
    set_constraint,
    remove_constraint,
    get_constraints,
    list_constraints,
    validate_value,
    VALID_TYPES,
)


@click.group(name="constraint")
def cmd_constraint():
    """Manage validation constraints on secret keys."""


@cmd_constraint.command(name="set")
@click.argument("key")
@click.argument("type", type=click.Choice(sorted(VALID_TYPES)))
@click.argument("value")
@click.option("--profile", default="default", show_default=True)
def constraint_set(key, type, value, profile):
    """Set a constraint on KEY (regex, min_length, max_length)."""
    vault_path = get_vault_path(profile)
    try:
        set_constraint(vault_path, key, type, value)
        click.echo(f"Constraint '{type}' set on '{key}'.")
    except ValueError as e:
        raise click.ClickException(str(e))


@cmd_constraint.command(name="remove")
@click.argument("key")
@click.argument("type", type=click.Choice(sorted(VALID_TYPES)))
@click.option("--profile", default="default", show_default=True)
def constraint_remove(key, type, profile):
    """Remove a specific constraint from KEY."""
    vault_path = get_vault_path(profile)
    removed = remove_constraint(vault_path, key, type)
    if removed:
        click.echo(f"Constraint '{type}' removed from '{key}'.")
    else:
        click.echo(f"No constraint '{type}' found on '{key}'.")


@cmd_constraint.command(name="list")
@click.option("--profile", default="default", show_default=True)
@click.argument("key", required=False)
def constraint_list(profile, key):
    """List constraints. Optionally filter by KEY."""
    vault_path = get_vault_path(profile)
    if key:
        data = {key: get_constraints(vault_path, key)}
    else:
        data = list_constraints(vault_path)
    if not data:
        click.echo("No constraints defined.")
        return
    for k, rules in sorted(data.items()):
        for ctype, cval in sorted(rules.items()):
            click.echo(f"{k}  {ctype}={cval}")


@cmd_constraint.command(name="check")
@click.argument("key")
@click.argument("value")
@click.option("--profile", default="default", show_default=True)
def constraint_check(key, value, profile):
    """Check VALUE against all constraints defined for KEY."""
    vault_path = get_vault_path(profile)
    errors = validate_value(vault_path, key, value)
    if not errors:
        click.echo("OK — value satisfies all constraints.")
    else:
        for err in errors:
            click.echo(f"FAIL: {err}")
        raise SystemExit(1)
