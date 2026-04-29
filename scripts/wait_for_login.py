#!/usr/bin/env python3
"""Wait until the local IBKR gateway reports an authenticated brokerage session."""

from __future__ import annotations

import argparse
import sys
import time
from typing import Any

import requests
import urllib3


def post_json(session: requests.Session, base_url: str, path: str) -> dict[str, Any]:
    response = session.post(f"{base_url}{path}", json={}, timeout=15)
    response.raise_for_status()
    payload = response.json()
    return payload if isinstance(payload, dict) else {}


def get_json(session: requests.Session, base_url: str, path: str) -> dict[str, Any]:
    response = session.get(f"{base_url}{path}", timeout=15)
    response.raise_for_status()
    payload = response.json()
    return payload if isinstance(payload, dict) else {}


def is_ready(session: requests.Session, base_url: str) -> tuple[bool, str]:
    try:
        auth_status = post_json(session, base_url, "/iserver/auth/status")
        if auth_status.get("authenticated") is True:
            return True, "brokerage session authenticated"
        if auth_status:
            connected = auth_status.get("connected")
            return False, f"brokerage auth pending; connected={connected}"
    except requests.RequestException as exc:
        last_error = f"auth status unavailable: {exc}"
    else:
        last_error = "auth status empty"

    try:
        sso_status = get_json(session, base_url, "/sso/validate")
        if sso_status.get("RESULT") is True:
            return False, "SSO valid; waiting for brokerage auth"
        if sso_status:
            return False, "SSO login pending"
    except requests.RequestException as exc:
        return False, f"{last_error}; SSO unavailable: {exc}"

    return False, last_error


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="https://localhost:5000/v1/api")
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--interval", type=int, default=5)
    args = parser.parse_args()

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    session = requests.Session()
    session.verify = False

    deadline = time.monotonic() + args.timeout
    last_message = ""

    while time.monotonic() < deadline:
        ready, message = is_ready(session, args.base_url)
        if ready:
            print(message)
            return 0

        if message != last_message:
            print(message)
            last_message = message

        time.sleep(args.interval)

    print(f"Timed out after {args.timeout}s waiting for IBKR login", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
