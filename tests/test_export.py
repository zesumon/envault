"""Tests for envault.export module."""

import pytest
from pathlib import Path
from envault.export import parse_dotenv, render_dotenv, export_to_file, import_from_file


def test_parse_dotenv_basic():
    content = "KEY=value\nANOTHER=hello"
    result = parse_dotenv(content)
    assert result == {"KEY": "value", "ANOTHER": "hello"}


def test_parse_dotenv_ignores_comments():
    content = "# this is a comment\nKEY=value"
    result = parse_dotenv(content)
    assert result == {"KEY": "value"}


def test_parse_dotenv_ignores_blank_lines():
    content = "\nKEY=value\n\n"
    result = parse_dotenv(content)
    assert result == {"KEY": "value"}


def test_parse_dotenv_strips_quotes():
    content = 'KEY="quoted value"\nOTHER=\'single\''
    result = parse_dotenv(content)
    assert result["KEY"] == "quoted value"
    assert result["OTHER"] == "single"


def test_parse_dotenv_value_with_equals():
    content = "KEY=val=ue"
    result = parse_dotenv(content)
    assert result["KEY"] == "val=ue"


def test_render_dotenv_basic():
    secrets = {"KEY": "value", "FOO": "bar"}
    output = render_dotenv(secrets)
    assert "FOO=bar" in output
    assert "KEY=value" in output


def test_render_dotenv_quotes_values_with_spaces():
    secrets = {"KEY": "hello world"}
    output = render_dotenv(secrets)
    assert 'KEY="hello world"' in output


def test_render_dotenv_with_comment():
    secrets = {"X": "1"}
    output = render_dotenv(secrets, comment="test comment")
    assert output.startswith("# test comment")


def test_export_and_import_roundtrip(tmp_path):
    secrets = {"DB_URL": "postgres://localhost/db", "SECRET_KEY": "abc123"}
    env_file = tmp_path / ".env"
    export_to_file(secrets, env_file)
    loaded = import_from_file(env_file)
    assert loaded == secrets


def test_export_raises_if_file_exists(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("EXISTING=true")
    with pytest.raises(FileExistsError):
        export_to_file({"KEY": "val"}, env_file, overwrite=False)


def test_export_overwrites_when_flag_set(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("OLD=true")
    export_to_file({"NEW": "value"}, env_file, overwrite=True)
    loaded = import_from_file(env_file)
    assert loaded == {"NEW": "value"}
    assert "OLD" not in loaded


def test_import_raises_if_file_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        import_from_file(tmp_path / "nonexistent.env")
