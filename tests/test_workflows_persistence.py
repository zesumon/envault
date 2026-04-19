import json
import pytest
from pathlib import Path
from envault.workflows import save_workflow, delete_workflow, _get_workflows_path


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


def test_workflows_file_is_valid_json(vault_dir):
    vault_path = vault_dir / "vault.db"
    save_workflow(vault_path, "w1", ["a", "b"])
    p = _get_workflows_path(vault_path)
    data = json.loads(p.read_text())
    assert "w1" in data


def test_multiple_workflows_persist(vault_dir):
    vault_path = vault_dir / "vault.db"
    save_workflow(vault_path, "w1", ["a"])
    save_workflow(vault_path, "w2", ["b", "c"])
    data = json.loads(_get_workflows_path(vault_path).read_text())
    assert "w1" in data and "w2" in data


def test_delete_leaves_others_intact(vault_dir):
    vault_path = vault_dir / "vault.db"
    save_workflow(vault_path, "keep", ["x"])
    save_workflow(vault_path, "drop", ["y"])
    delete_workflow(vault_path, "drop")
    data = json.loads(_get_workflows_path(vault_path).read_text())
    assert "keep" in data
    assert "drop" not in data


def test_overwrite_updates_steps_in_file(vault_dir):
    vault_path = vault_dir / "vault.db"
    save_workflow(vault_path, "w", ["old"])
    save_workflow(vault_path, "w", ["new"])
    data = json.loads(_get_workflows_path(vault_path).read_text())
    assert data["w"]["steps"] == ["new"]
