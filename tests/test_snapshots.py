"""Tests for envault.snapshots."""

import pytest

from envault.snapshots import (
    list_snapshots,
    create_snapshot,
    restore_snapshot,
    delete_snapshot,
)
from envault.storage import set_secret, get_secret


PASSWORD = "test-pass"


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def _populate(vault_dir, keys: dict):
    for k, v in keys.items():
        set_secret(k, v, PASSWORD, vault_dir=vault_dir)


def test_list_snapshots_empty(vault_dir):
    assert list_snapshots(vault_dir=vault_dir) == []


def test_create_snapshot_returns_name(vault_dir):
    _populate(vault_dir, {"KEY": "val"})
    name = create_snapshot(PASSWORD, vault_dir=vault_dir)
    assert isinstance(name, str)
    assert len(name) > 0


def test_create_snapshot_appears_in_list(vault_dir):
    _populate(vault_dir, {"KEY": "val"})
    name = create_snapshot(PASSWORD, name="snap1", vault_dir=vault_dir)
    assert name in list_snapshots(vault_dir=vault_dir)


def test_create_duplicate_snapshot_raises(vault_dir):
    _populate(vault_dir, {"KEY": "val"})
    create_snapshot(PASSWORD, name="dup", vault_dir=vault_dir)
    with pytest.raises(ValueError, match="already exists"):
        create_snapshot(PASSWORD, name="dup", vault_dir=vault_dir)


def test_restore_snapshot_overwrites_vault(vault_dir):
    _populate(vault_dir, {"ORIGINAL": "yes"})
    create_snapshot(PASSWORD, name="before", vault_dir=vault_dir)

    # Change vault after snapshot
    set_secret("ORIGINAL", "changed", PASSWORD, vault_dir=vault_dir)
    set_secret("EXTRA", "extra", PASSWORD, vault_dir=vault_dir)

    count = restore_snapshot("before", PASSWORD, vault_dir=vault_dir)
    assert count == 1
    assert get_secret("ORIGINAL", PASSWORD, vault_dir=vault_dir) == "yes"
    assert get_secret("EXTRA", PASSWORD, vault_dir=vault_dir) is None


def test_restore_missing_snapshot_raises(vault_dir):
    with pytest.raises(FileNotFoundError):
        restore_snapshot("nope", PASSWORD, vault_dir=vault_dir)


def test_delete_snapshot_removes_from_list(vault_dir):
    _populate(vault_dir, {"K": "v"})
    create_snapshot(PASSWORD, name="to_del", vault_dir=vault_dir)
    delete_snapshot("to_del", vault_dir=vault_dir)
    assert "to_del" not in list_snapshots(vault_dir=vault_dir)


def test_delete_missing_snapshot_raises(vault_dir):
    with pytest.raises(FileNotFoundError):
        delete_snapshot("ghost", vault_dir=vault_dir)


def test_list_snapshots_sorted_newest_first(vault_dir):
    _populate(vault_dir, {"K": "v"})
    create_snapshot(PASSWORD, name="aaa", vault_dir=vault_dir)
    create_snapshot(PASSWORD, name="zzz", vault_dir=vault_dir)
    snaps = list_snapshots(vault_dir=vault_dir)
    assert snaps[0] == "zzz"
    assert snaps[1] == "aaa"
