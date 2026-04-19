import pytest
from pathlib import Path
from envault.ratings import set_rating, get_rating, remove_rating, list_ratings
from envault.storage import save_vault


@pytest.fixture
def vault_path(tmp_path):
    vp = tmp_path / "vault" / "vault.enc"
    vp.parent.mkdir(parents=True)
    save_vault(vp, {}, "pass")
    return vp


def test_get_rating_returns_none_when_no_file(vault_path):
    assert get_rating(vault_path, "MY_KEY") is None


def test_set_and_get_rating(vault_path):
    set_rating(vault_path, "API_KEY", 5)
    assert get_rating(vault_path, "API_KEY") == 5


def test_set_rating_invalid_raises(vault_path):
    with pytest.raises(ValueError, match="Rating must be 1-5"):
        set_rating(vault_path, "API_KEY", 0)
    with pytest.raises(ValueError):
        set_rating(vault_path, "API_KEY", 6)


def test_set_rating_overwrites_existing(vault_path):
    set_rating(vault_path, "DB_PASS", 3)
    set_rating(vault_path, "DB_PASS", 1)
    assert get_rating(vault_path, "DB_PASS") == 1


def test_remove_rating_returns_true_when_exists(vault_path):
    set_rating(vault_path, "TOKEN", 4)
    assert remove_rating(vault_path, "TOKEN") is True
    assert get_rating(vault_path, "TOKEN") is None


def test_remove_rating_returns_false_when_missing(vault_path):
    assert remove_rating(vault_path, "GHOST") is False


def test_list_ratings_empty(vault_path):
    assert list_ratings(vault_path) == {}


def test_list_ratings_returns_sorted(vault_path):
    set_rating(vault_path, "Z_KEY", 2)
    set_rating(vault_path, "A_KEY", 5)
    set_rating(vault_path, "M_KEY", 3)
    result = list_ratings(vault_path)
    assert list(result.keys()) == ["A_KEY", "M_KEY", "Z_KEY"]
    assert result["A_KEY"] == 5


def test_ratings_all_valid_values(vault_path):
    for r in range(1, 6):
        set_rating(vault_path, f"KEY_{r}", r)
        assert get_rating(vault_path, f"KEY_{r}") == r
