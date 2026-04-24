"""Vault usage metrics — counts, sizes, and activity summaries."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List

from envault.storage import load_vault, get_vault_path
from envault.audit import read_events
from envault.tags import get_tags
from envault.history import get_key_history


@dataclass
class VaultMetrics:
    total_keys: int = 0
    total_size_bytes: int = 0
    avg_value_length: float = 0.0
    keys_with_tags: int = 0
    keys_with_history: int = 0
    total_audit_events: int = 0
    most_recent_action: str = ""
    action_counts: Dict[str, int] = field(default_factory=dict)
    top_keys_by_history: List[str] = field(default_factory=list)


def compute_metrics(vault_path: str, password: str) -> VaultMetrics:
    """Compute usage metrics for the vault at *vault_path*."""
    vault = load_vault(vault_path, password)
    keys = list(vault.keys())
    m = VaultMetrics()

    m.total_keys = len(keys)

    if keys:
        lengths = [len(vault[k]) for k in keys]
        m.total_size_bytes = sum(lengths)
        m.avg_value_length = round(m.total_size_bytes / len(keys), 2)

        tagged = sum(1 for k in keys if get_tags(vault_path, k))
        m.keys_with_tags = tagged

        history_counts: Dict[str, int] = {}
        for k in keys:
            h = get_key_history(vault_path, k)
            if h:
                m.keys_with_history += 1
                history_counts[k] = len(h)

        m.top_keys_by_history = sorted(
            history_counts, key=lambda k: history_counts[k], reverse=True
        )[:5]

    events = read_events(vault_path)
    m.total_audit_events = len(events)
    if events:
        m.most_recent_action = events[-1].get("action", "")
        for ev in events:
            action = ev.get("action", "unknown")
            m.action_counts[action] = m.action_counts.get(action, 0) + 1

    return m


def format_metrics(m: VaultMetrics) -> str:
    """Return a human-readable summary of *m*."""
    lines = [
        f"Keys            : {m.total_keys}",
        f"Total size      : {m.total_size_bytes} bytes",
        f"Avg value len   : {m.avg_value_length}",
        f"Keys with tags  : {m.keys_with_tags}",
        f"Keys w/ history : {m.keys_with_history}",
        f"Audit events    : {m.total_audit_events}",
        f"Last action     : {m.most_recent_action or 'n/a'}",
    ]
    if m.action_counts:
        lines.append("Action breakdown:")
        for action, count in sorted(m.action_counts.items()):
            lines.append(f"  {action:<16}: {count}")
    if m.top_keys_by_history:
        lines.append("Top keys by history: " + ", ".join(m.top_keys_by_history))
    return "\n".join(lines)
