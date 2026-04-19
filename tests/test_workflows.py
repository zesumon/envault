import pytest
from pathlib import Path
from envault.workflows import (
    list_workflows, save_workflow, get_workflow,
    delete_workflow, rename_workflow,
)


@pytest.fixture
def vault_path(tmp_path):
    return tmp_path / "vault.db"


def test_list_workflows_empty_when_no_file(vault_path):
    assert list_workflows(vault_path) == []


def test_save_and_list_workflow(vault_path):
    save_workflow(vault_path, "deploy", ["export", "sync", "push"])
    assert "deploy" in list_workflows(vault_path)


def test_list_workflows_sorted(vault_path):
    save_workflow(vault_path, "zebra", ["a"])
    save_workflow(vault_path, "alpha", ["b"])
    assert list_workflows(vault_path) == ["alpha", "zebra"]


def test_get_workflow_returns_steps(vault_path):
    save_workflow(vault_path, "setup", ["init", "import"])
    assert get_workflow(vault_path, "setup") == ["init", "import"]


def test_get_workflow_missing_returns_none(vault_path):
    assert get_workflow(vault_path, "ghost") is None


def test_save_workflow_invalid_name_raises(vault_path):
    with pytest.raises(ValueError):
        save_workflow(vault_path, "bad name!", ["step"])


def test_save_workflow_empty_steps_raises(vault_path):
    with pytest.raises(ValueError):
        save_workflow(vault_path, "empty", [])


def test_delete_workflow_returns_true(vault_path):
    save_workflow(vault_path, "tmp", ["x"])
    assert delete_workflow(vault_path, "tmp") is True
    assert get_workflow(vault_path, "tmp") is None


def test_delete_missing_workflow_returns_false(vault_path):
    assert delete_workflow(vault_path, "nope") is False


def test_rename_workflow(vault_path):
    save_workflow(vault_path, "old", ["step1"])
    rename_workflow(vault_path, "old", "new")
    assert get_workflow(vault_path, "new") == ["step1"]
    assert get_workflow(vault_path, "old") is None


def test_rename_missing_workflow_raises(vault_path):
    with pytest.raises(KeyError):
        rename_workflow(vault_path, "ghost", "new")


def test_rename_to_existing_raises(vault_path):
    save_workflow(vault_path, "a", ["1"])
    save_workflow(vault_path, "b", ["2"])
    with pytest.raises(ValueError):
        rename_workflow(vault_path, "a", "b")


def test_overwrite_workflow_updates_steps(vault_path):
    save_workflow(vault_path, "w", ["old"])
    save_workflow(vault_path, "w", ["new1", "new2"])
    assert get_workflow(vault_path, "w") == ["new1", "new2"]
