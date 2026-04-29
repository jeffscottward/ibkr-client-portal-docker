"""Output redaction for sensitive IBKR gateway fields."""

from __future__ import annotations

from typing import Any


REDACTED = "[REDACTED]"
SENSITIVE_KEY_PARTS = (
    "account",
    "acct",
    "credential",
    "desc",
    "display",
    "hardware",
    "id",
    "ip",
    "mac",
    "session",
    "token",
    "user",
    "van",
)


def is_sensitive_key(key: object) -> bool:
    key_text = str(key).lower()
    return any(part in key_text for part in SENSITIVE_KEY_PARTS)


def redact_sensitive(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: REDACTED if is_sensitive_key(key) else redact_sensitive(child)
            for key, child in value.items()
        }

    if isinstance(value, list):
        return [redact_sensitive(child) for child in value]

    return value
