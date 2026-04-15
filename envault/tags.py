"""Tag-based grouping and filtering of secrets."""

from __future__ import annotations

from typing import Dict, List, Optional

from envault.storage import load_vault, save_vault


TAGS_META_KEY = "__tags__"


def _load_tags(vault_path: str, password: str) -> Dict[str, List[str]]:
    """Return the tags mapping {key: [tag, ...]} from the vault."""
    vault = load_vault(vault_path, password)
    raw = vault.get(TAGS_META_KEY, {})
    if not isinstance(raw, dict):
        return {}
    return raw


def _save_tags(vault_path: str, password: str, tags: Dict[str, List[str]]) -> None:
    vault = load_vault(vault_path, password)
    vault[TAGS_META_KEY] = tags
    save_vault(vault_path, password, vault)


def add_tag(vault_path: str, password: str, key: str, tag: str) -> None:
    """Add *tag* to *key*. Raises KeyError if the secret key doesn't exist."""
    vault = load_vault(vault_path, password)
    if key not in vault or key == TAGS_META_KEY:
        raise KeyError(f"Secret '{key}' not found.")
    tags = _load_tags(vault_path, password)
    existing = tags.get(key, [])
    if tag not in existing:
        existing.append(tag)
    tags[key] = existing
    _save_tags(vault_path, password, tags)


def remove_tag(vault_path: str, password: str, key: str, tag: str) -> bool:
    """Remove *tag* from *key*. Returns True if removed, False if not present."""
    tags = _load_tags(vault_path, password)
    existing = tags.get(key, [])
    if tag not in existing:
        return False
    existing.remove(tag)
    tags[key] = existing
    _save_tags(vault_path, password, tags)
    return True


def get_tags(vault_path: str, password: str, key: str) -> List[str]:
    """Return list of tags for *key*."""
    tags = _load_tags(vault_path, password)
    return tags.get(key, [])


def keys_by_tag(vault_path: str, password: str, tag: str) -> List[str]:
    """Return sorted list of secret keys that carry *tag*."""
    tags = _load_tags(vault_path, password)
    return sorted(k for k, v in tags.items() if tag in v)


def all_tags(vault_path: str, password: str) -> List[str]:
    """Return a sorted, deduplicated list of every tag in use."""
    tags = _load_tags(vault_path, password)
    seen: set = set()
    for tag_list in tags.values():
        seen.update(tag_list)
    return sorted(seen)
