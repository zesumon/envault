"""Tests for envault.notes module."""

import pytest
from pathlib import Path
from envault.notes import set_note, get_note, delete_note, list_notes, clear_notes


@pytest.fixture
def vault_path(tmp_path):
    return tmp_path / ".envault" / "vault.enc"


def test_get_note_returns_none_when_no_file(vault_path):
    assert get_note(vault_path, "API_KEY") is None


def test_set_and_get_note(vault_path):
    set_note(vault_path, "API_KEY", "Production API key for Stripe")
    assert get_note(vault_path, "API_KEY") == "Production API key for Stripe"


def test_get_note_missing_key_returns_none(vault_path):
    set_note(vault_path, "DB_URL", "Main database")
    assert get_note(vault_path, "MISSING_KEY") is None


def test_set_note_overwrites_existing(vault_path):
    set_note(vault_path, "TOKEN", "old note")
    set_note(vault_path, "TOKEN", "new note")
    assert get_note(vault_path, "TOKEN") == "new note"


def test_delete_note_returns_true_when_exists(vault_path):
    set_note(vault_path, "SECRET", "some note")
    assert delete_note(vault_path, "SECRET") is True
    assert get_note(vault_path, "SECRET") is None


def test_delete_note_returns_false_when_missing(vault_path):
    assert delete_note(vault_path, "NONEXISTENT") is False


def test_list_notes_empty(vault_path):
    assert list_notes(vault_path) == {}


def test_list_notes_returns_all(vault_path):
    set_note(vault_path, "KEY_A", "note a")
    set_note(vault_path, "KEY_B", "note b")
    result = list_notes(vault_path)
    assert result == {"KEY_A": "note a", "KEY_B": "note b"}


def test_list_notes_is_a_copy(vault_path):
    set_note(vault_path, "X", "val")
    result = list_notes(vault_path)
    result["X"] = "mutated"
    assert get_note(vault_path, "X") == "val"


def test_clear_notes_returns_count(vault_path):
    set_note(vault_path, "A", "1")
    set_note(vault_path, "B", "2")
    assert clear_notes(vault_path) == 2


def test_clear_notes_removes_all(vault_path):
    set_note(vault_path, "A", "1")
    clear_notes(vault_path)
    assert list_notes(vault_path) == {}


def test_clear_notes_empty_vault_returns_zero(vault_path):
    assert clear_notes(vault_path) == 0
