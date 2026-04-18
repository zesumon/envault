import pytest
from pathlib import Path
from envault import schema as sc


@pytest.fixture
def vault_path(tmp_path):
    return tmp_path / "vault" / "vault.enc"


def test_list_schema_empty_when_no_file(vault_path):
    assert sc.list_schema(vault_path) == {}


def test_set_and_get_schema(vault_path):
    sc.set_schema(vault_path, "PORT", "integer")
    rule = sc.get_schema(vault_path, "PORT")
    assert rule["type"] == "integer"
    assert rule["required"] is False


def test_set_schema_required(vault_path):
    sc.set_schema(vault_path, "API_KEY", "string", required=True)
    rule = sc.get_schema(vault_path, "API_KEY")
    assert rule["required"] is True


def test_set_schema_invalid_type_raises(vault_path):
    with pytest.raises(ValueError, match="Invalid type"):
        sc.set_schema(vault_path, "FOO", "banana")


def test_set_schema_with_pattern(vault_path):
    sc.set_schema(vault_path, "CODE", "string", pattern=r"^[A-Z]{3}$")
    rule = sc.get_schema(vault_path, "CODE")
    assert rule["pattern"] == r"^[A-Z]{3}$"


def test_set_schema_invalid_pattern_raises(vault_path):
    with pytest.raises(Exception):
        sc.set_schema(vault_path, "X", "string", pattern="[invalid")


def test_remove_schema_existing(vault_path):
    sc.set_schema(vault_path, "HOST", "string")
    assert sc.remove_schema(vault_path, "HOST") is True
    assert sc.get_schema(vault_path, "HOST") is None


def test_remove_schema_missing_returns_false(vault_path):
    assert sc.remove_schema(vault_path, "NOPE") is False


def test_validate_value_integer_ok(vault_path):
    sc.set_schema(vault_path, "PORT", "integer")
    assert sc.validate_value(vault_path, "PORT", "8080") == []


def test_validate_value_integer_fail(vault_path):
    sc.set_schema(vault_path, "PORT", "integer")
    errs = sc.validate_value(vault_path, "PORT", "not-a-number")
    assert len(errs) == 1


def test_validate_value_url_ok(vault_path):
    sc.set_schema(vault_path, "ENDPOINT", "url")
    assert sc.validate_value(vault_path, "ENDPOINT", "https://example.com") == []


def test_validate_value_email_fail(vault_path):
    sc.set_schema(vault_path, "EMAIL", "email")
    errs = sc.validate_value(vault_path, "EMAIL", "not-an-email")
    assert errs


def test_validate_value_custom_pattern_fail(vault_path):
    sc.set_schema(vault_path, "CODE", "string", pattern=r"^[A-Z]{3}$")
    errs = sc.validate_value(vault_path, "CODE", "abc")
    assert errs


def test_validate_required_detects_missing(vault_path):
    sc.set_schema(vault_path, "DB_URL", "string", required=True)
    sc.set_schema(vault_path, "PORT", "integer", required=False)
    missing = sc.validate_required(vault_path, {"PORT"})
    assert "DB_URL" in missing
    assert "PORT" not in missing


def test_validate_no_schema_always_passes(vault_path):
    assert sc.validate_value(vault_path, "ANYTHING", "whatever") == []
