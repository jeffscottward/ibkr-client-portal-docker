"""Readiness checks for gateway and brokerage sessions."""

from __future__ import annotations

import sys
import time
from collections.abc import Callable
from typing import Protocol

import requests


class AuthClient(Protocol):
    def post_json(self, path: str, json_body: object | None = None) -> dict[str, object]: ...

    def get_json(self, path: str) -> dict[str, object]: ...


class HttpSession(Protocol):
    verify: bool

    def get(self, url: str, timeout: float) -> requests.Response: ...


def describe_brokerage_readiness(client: AuthClient) -> tuple[bool, str]:
    try:
        auth_status = client.post_json("/iserver/auth/status")
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
        sso_status = client.get_json("/sso/validate")
        if sso_status.get("RESULT") is True:
            return False, "SSO valid; waiting for brokerage auth"
        if sso_status:
            return False, "SSO login pending"
    except requests.RequestException as exc:
        return False, f"{last_error}; SSO unavailable: {exc}"

    return False, last_error


def wait_for_brokerage_auth(
    client: AuthClient,
    *,
    timeout_seconds: int,
    interval_seconds: int,
    on_message: Callable[[str], None] = print,
    sleep: Callable[[float], None] = time.sleep,
    monotonic: Callable[[], float] = time.monotonic,
) -> bool:
    deadline = monotonic() + timeout_seconds
    last_message = ""

    while monotonic() < deadline:
        ready, message = describe_brokerage_readiness(client)
        if ready:
            on_message(message)
            return True

        if message != last_message:
            on_message(message)
            last_message = message

        sleep(interval_seconds)

    print(f"Timed out after {timeout_seconds}s waiting for IBKR login", file=sys.stderr)
    return False


def wait_for_gateway(
    session: HttpSession,
    *,
    url: str,
    timeout_seconds: int,
    interval_seconds: int,
    on_message: Callable[[str], None] = print,
    sleep: Callable[[float], None] = time.sleep,
    monotonic: Callable[[], float] = time.monotonic,
) -> bool:
    deadline = monotonic() + timeout_seconds
    last_message = ""

    while monotonic() < deadline:
        try:
            response = session.get(url, timeout=10)
            on_message(f"Gateway reachable: HTTP {response.status_code}")
            return True
        except requests.RequestException as exc:
            message = f"Gateway not ready: {exc.__class__.__name__}"
            if message != last_message:
                on_message(message)
                last_message = message

        sleep(interval_seconds)

    print(f"Timed out after {timeout_seconds}s waiting for gateway", file=sys.stderr)
    return False
