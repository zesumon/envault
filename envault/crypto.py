"""Encryption and decryption utilities for envault using AES-GCM."""

import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32
ITERATIONS = 200_000


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a 256-bit key from a password using PBKDF2-SHA256."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=ITERATIONS,
    )
    return kdf.derive(password.encode())


def encrypt(plaintext: str, password: str) -> str:
    """Encrypt plaintext with a password. Returns a base64-encoded blob."""
    salt = os.urandom(SALT_SIZE)
    nonce = os.urandom(NONCE_SIZE)
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
    blob = salt + nonce + ciphertext
    return base64.b64encode(blob).decode()


def decrypt(encoded_blob: str, password: str) -> str:
    """Decrypt a base64-encoded blob with a password. Returns plaintext."""
    blob = base64.b64decode(encoded_blob.encode())
    salt = blob[:SALT_SIZE]
    nonce = blob[SALT_SIZE:SALT_SIZE + NONCE_SIZE]
    ciphertext = blob[SALT_SIZE + NONCE_SIZE:]
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None).decode()
