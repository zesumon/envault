"""Tests for envault crypto module."""

import pytest
from cryptography.exceptions import InvalidTag
from envault.crypto import encrypt, decrypt


PASSWORD = "super-secret-passphrase"
PLAINTEXT = "DB_HOST=localhost\nDB_PASS=hunter2\nAPI_KEY=abc123"


def test_encrypt_returns_string():
    result = encrypt(PLAINTEXT, PASSWORD)
    assert isinstance(result, str)
    assert len(result) > 0


def test_decrypt_roundtrip():
    blob = encrypt(PLAINTEXT, PASSWORD)
    recovered = decrypt(blob, PASSWORD)
    assert recovered == PLAINTEXT


def test_encrypt_produces_unique_blobs():
    blob1 = encrypt(PLAINTEXT, PASSWORD)
    blob2 = encrypt(PLAINTEXT, PASSWORD)
    # Different nonces/salts mean different ciphertexts
    assert blob1 != blob2


def test_decrypt_wrong_password_raises():
    blob = encrypt(PLAINTEXT, PASSWORD)
    with pytest.raises(InvalidTag):
        decrypt(blob, "wrong-password")


def test_decrypt_tampered_blob_raises():
    blob = encrypt(PLAINTEXT, PASSWORD)
    tampered = blob[:-4] + "XXXX"
    with pytest.raises(Exception):
        decrypt(tampered, PASSWORD)


def test_encrypt_empty_string():
    blob = encrypt("", PASSWORD)
    assert decrypt(blob, PASSWORD) == ""


def test_encrypt_unicode_content():
    text = "SECRET=café☕\nNAME=José"
    blob = encrypt(text, PASSWORD)
    assert decrypt(blob, PASSWORD) == text
