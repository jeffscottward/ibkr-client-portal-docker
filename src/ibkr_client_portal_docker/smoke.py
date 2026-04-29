"""Read-only smoke checks against an authenticated IBKR gateway."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

import requests

from .config import Endpoint, SMOKE_CHECKS
from .redaction import redact_sensitive


class JsonClient(Protocol):
    def request_json(self, method: str, path: str, *, json_body: object | None = None) -> Any: ...


@dataclass(frozen=True)
class SmokeResult:
    name: str
    ok: bool
    payload: Any | None = None
    error: str | None = None
    status_code: int | None = None


def run_smoke_checks(client: JsonClient, checks: tuple[Endpoint, ...] = SMOKE_CHECKS) -> list[SmokeResult]:
    results: list[SmokeResult] = []

    for check in checks:
        try:
            payload = client.request_json(
                check.method,
                check.path,
                json_body={} if check.method == "POST" else None,
            )
            results.append(SmokeResult(check.name, True, redact_sensitive(payload)))
        except requests.HTTPError as exc:
            results.append(
                SmokeResult(
                    check.name,
                    False,
                    error=exc.response.text,
                    status_code=exc.response.status_code,
                )
            )
        except requests.RequestException as exc:
            results.append(SmokeResult(check.name, False, error=str(exc)))

    return results
