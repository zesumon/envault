"""Persistence tests for mentions feature."""
import json
import pytest
from pathlib import Path
from envault.mentions import add_mention, get_mentions, _get_mentions_path
from envault.storage import save_vault


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


def _vault(vault_dir):
    return vault_dir / "secrets.vault"


def _add_key(vault_dir, key):
    vp = _vault(vault_dir)
    from envault.storage import load_vault
    v = load_vault(vp, "pw")
    v[key] = "x"
    save_vault(vp, v, "pw")


def test_mentions_file_is_valid_json(vault_dir):
    _add_key(vault_dir, "K")
    add_mention(_vault(vault_dir), "K", "REF")
    p = _get_mentions_path(_vault(vault_dir))
    data = json.loads(p.read_text())
    assert isinstance(data, dict)


def test_multiple_mentions_persist(vault_dir):
    _add_key(vault_dir, "A")
    _add_key(vault_dir, "B")
    add_mention(_vault(vault_dir), "A", "R1")
    add_mention(_vault(vault_dir), "B", "R2")
    assert "R1" in get_mentions(_vault(vault_dir), "A")
    assert "R2" in get_mentions(_vault(vault_dir), "B")


def test_mentions_sorted_alphabetically(vault_dir):
    _add_key(vault_dir, "K")
    add_mention(_vault(vault_dir), "K", "Z_REF")
    add_mention(_vault(vault_dir), "K", "A_REF")
    refs = get_mentions(_vault(vault_dir), "K")
    assert refs == sorted(refs)


def test_remove_leaves_others_intact(vault_dir):
    _add_key(vault_dir, "K")
    from envault.mentions import remove_mention
    add_mention(_vault(vault_dir), "K", "R1")
    add_mention(_vault(vault_dir), "K", "R2")
    remove_mention(_vault(vault_dir), "K", "R1")
    assert get_mentions(_vault(vault_dir), "K") == ["R2"]
