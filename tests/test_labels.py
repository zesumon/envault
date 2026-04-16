"""Tests for envault.labels."""
import pytest
from pathlib import Path
from envault.labels import set_label, get_label, remove_label, list_labels


@pytest.fixture
def vault_path(tmp_path):
    return tmp_path / "vault" / "default.vault"


def test_get_label_returns_none_when_no_file(vault_path):
    assert get_label(vault_path, "FOO") is None


def test_set_and_get_label(vault_path):
    set_label(vault_path, "API_KEY", "Main API key")
    assert get_label(vault_path, "API_KEY") == "Main API key"


def test_set_label_overwrites_existing(vault_path):
    set_label(vault_path, "DB_PASS", "old")
    set_label(vault_path, "DB_PASS", "new")
    assert get_label(vault_path, "DB_PASS") == "new"


def test_get_label_missing_key_returns_none(vault_path):
    set_label(vault_path, "A", "alpha")
    assert get_label(vault_path, "B") is None


def test_remove_label_returns_true_when_exists(vault_path):
    set_label(vault_path, "X", "ex")
    assert remove_label(vault_path, "X") is True
    assert get_label(vault_path, "X") is None


def test_remove_label_returns_false_when_missing(vault_path):
    assert remove_label(vault_path, "GHOST") is False


def test_list_labels_empty(vault_path):
    assert list_labels(vault_path) == {}


def test_list_labels_sorted(vault_path):
    set_label(vault_path, "Z_KEY", "z")
    set_label(vault_path, "A_KEY", "a")
    set_label(vault_path, "M_KEY", "m")
    keys = list(list_labels(vault_path).keys())
    assert keys == sorted(keys)


def test_labels_file_is_valid_json(vault_path, tmp_path):
    import json
    set_label(vault_path, "FOO", "bar")
    labels_file = vault_path.parent / "labels.json"
    data = json.loads(labels_file.read_text())
    assert data["FOO"] == "bar"
