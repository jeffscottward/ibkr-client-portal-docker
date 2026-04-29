#!/usr/bin/env python3
"""Read-only checks for an authenticated local IBKR Client Portal Gateway."""

from __future__ import annotations

import argparse
import json
from typing import Any

import requests
import urllib3


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


def redact_sensitive(value: Any) -> Any:
    if isinstance(value, dict):
        redacted = {}
        for key, child in value.items():
            key_text = str(key).lower()
            if any(part in key_text for part in SENSITIVE_KEY_PARTS):
                redacted[key] = "[REDACTED]"
            else:
                redacted[key] = redact_sensitive(child)
        return redacted

    if isinstance(value, list):
        return [redact_sensitive(child) for child in value]

    return value


def request_json(session: requests.Session, method: str, base_url: str, path: str) -> Any:
    response = session.request(method, f"{base_url}{path}", json={} if method == "POST" else None, timeout=15)
    response.raise_for_status()
    return response.json()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="https://localhost:5000/v1/api")
    args = parser.parse_args()

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    session = requests.Session()
    session.verify = False

    checks = (
        ("sso_validate", "GET", "/sso/validate"),
        ("auth_status", "POST", "/iserver/auth/status"),
        ("tickle", "GET", "/tickle"),
        ("portfolio_accounts", "GET", "/portfolio/accounts"),
    )

    for name, method, path in checks:
        print(f"\n## {name}")
        try:
            payload = request_json(session, method, args.base_url, path)
            print(json.dumps(redact_sensitive(payload), indent=2, sort_keys=True))
        except requests.HTTPError as exc:
            print(f"HTTP {exc.response.status_code}: {exc.response.text}")
        except requests.RequestException as exc:
            print(f"Request failed: {exc}")


if __name__ == "__main__":
    main()
