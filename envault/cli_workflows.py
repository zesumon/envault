"""CLI commands for workflow management."""
import click
from pathlib import Path
from envault.storage import get_vault_path
from envault import workflows


@click.group("workflow")
def cmd_workflow():
    """Manage named operation workflows."""


@cmd_workflow.command("list")
def workflow_list():
    """List all saved workflows."""
    vault_path = Path(get_vault_path())
    names = workflows.list_workflows(vault_path)
    if not names:
        click.echo("No workflows saved.")
    else:
        for n in names:
            click.echo(n)


@cmd_workflow.command("save")
@click.argument("name")
@click.argument("steps", nargs=-1, required=True)
def workflow_save(name, steps):
    """Save a workflow with ordered STEPS."""
    vault_path = Path(get_vault_path())
    try:
        workflows.save_workflow(vault_path, name, list(steps))
        click.echo(f"Workflow '{name}' saved with {len(steps)} step(s).")
    except ValueError as e:
        raise click.ClickException(str(e))


@cmd_workflow.command("show")
@click.argument("name")
def workflow_show(name):
    """Show steps in a workflow."""
    vault_path = Path(get_vault_path())
    steps = workflows.get_workflow(vault_path, name)
    if steps is None:
        raise click.ClickException(f"Workflow '{name}' not found.")
    for i, step in enumerate(steps, 1):
        click.echo(f"  {i}. {step}")


@cmd_workflow.command("delete")
@click.argument("name")
def workflow_delete(name):
    """Delete a workflow."""
    vault_path = Path(get_vault_path())
    if not workflows.delete_workflow(vault_path, name):
        raise click.ClickException(f"Workflow '{name}' not found.")
    click.echo(f"Workflow '{name}' deleted.")


@cmd_workflow.command("rename")
@click.argument("old")
@click.argument("new")
def workflow_rename(old, new):
    """Rename a workflow."""
    vault_path = Path(get_vault_path())
    try:
        workflows.rename_workflow(vault_path, old, new)
        click.echo(f"Renamed '{old}' -> '{new}'.")
    except (KeyError, ValueError) as e:
        raise click.ClickException(str(e))
