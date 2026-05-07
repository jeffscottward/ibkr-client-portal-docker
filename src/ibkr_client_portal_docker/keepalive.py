"""Keep an authenticated IBKR gateway session warm."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

import requests


class TickleClient(Protocol):
    def get_json(self, path: str) -> dict[str, object]: ...


@dataclass(frozen=True)
class KeepaliveResult:
    ok: bool
    message: str


def tickle_gateway(client: TickleClient) -> KeepaliveResult:
    """Call /tickle and return a log-safe status summary."""

    try:
        payload = client.get_json("/tickle")
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else "unknown"
        return KeepaliveResult(False, f"tickle failed: HTTP {status_code}")
    except requests.RequestException as exc:
        return KeepaliveResult(False, f"tickle failed: {exc.__class__.__name__}")

    auth_status = {}
    iserver = payload.get("iserver")
    if isinstance(iserver, dict):
        candidate = iserver.get("authStatus")
        if isinstance(candidate, dict):
            auth_status = candidate

    authenticated = auth_status.get("authenticated")
    connected = auth_status.get("connected")
    sso_expires = payload.get("ssoExpires")

    ok = authenticated is True
    return KeepaliveResult(
        ok,
        f"tickle ok; authenticated={authenticated}; connected={connected}; ssoExpires={sso_expires}",
    )


def timestamped(message: str) -> str:
    return f"{datetime.now(UTC).isoformat()} {message}"


def run_keepalive(
    client: TickleClient,
    *,
    interval_seconds: int,
    once: bool = False,
    on_message: Callable[[str], None] = print,
    sleep: Callable[[float], None] = time.sleep,
) -> int:
    if interval_seconds < 1:
        raise ValueError("interval_seconds must be at least 1")

    while True:
        result = tickle_gateway(client)
        on_message(timestamped(result.message))

        if once:
            return 0 if result.ok else 1

        sleep(interval_seconds)
