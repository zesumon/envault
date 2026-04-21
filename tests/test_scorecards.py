"""Tests for envault.scorecards."""

import pytest
from pathlib import Path

from envault.storage import save_vault, get_vault_path
from envault.scorecards import compute_score, get_latest_scorecard
from envault.checksums import record_checksum

PASSWORD = "test-pass"


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / ".envault" / "default" / "vault.enc"


def _populate(vault_path: Path, secrets: dict) -> None:
    save_vault(vault_path, PASSWORD, secrets)
    for key, value in secrets.items():
        record_checksum(vault_path, key, value)


def test_compute_score_empty_vault_returns_100(vault_path: Path) -> None:
    save_vault(vault_path, PASSWORD, {})
    report = compute_score(vault_path, PASSWORD)
    assert report["score"] == 100
    assert report["total_keys"] == 0


def test_compute_score_returns_dict_with_expected_keys(vault_path: Path) -> None:
    _populate(vault_path, {"API_KEY": "abc123"})
    report = compute_score(vault_path, PASSWORD)
    assert "score" in report
    assert "total_keys" in report
    assert "issues" in report
    assert "breakdown" in report


def test_compute_score_is_between_0_and_100(vault_path: Path) -> None:
    _populate(vault_path, {"A": "val", "B": "other"})
    report = compute_score(vault_path, PASSWORD)
    assert 0 <= report["score"] <= 100


def test_compute_score_persists_latest(vault_path: Path) -> None:
    _populate(vault_path, {"X": "value"})
    compute_score(vault_path, PASSWORD)
    cached = get_latest_scorecard(vault_path)
    assert cached is not None
    assert "score" in cached


def test_get_latest_scorecard_returns_none_when_no_file(vault_path: Path) -> None:
    result = get_latest_scorecard(vault_path)
    assert result is None


def test_checksum_failure_reduces_score(vault_path: Path) -> None:
    # Save vault with a key but record a *different* value as checksum -> mismatch
    save_vault(vault_path, PASSWORD, {"SECRET": "real_value"})
    record_checksum(vault_path, "SECRET", "wrong_value")  # deliberate mismatch
    report = compute_score(vault_path, PASSWORD)
    assert report["breakdown"]["checksum_failures"] == 1
    assert report["score"] < 100


def test_compute_score_total_keys_matches(vault_path: Path) -> None:
    secrets = {f"KEY_{i}": f"val_{i}" for i in range(5)}
    _populate(vault_path, secrets)
    report = compute_score(vault_path, PASSWORD)
    assert report["total_keys"] == 5
