"""HTTP client helpers for the local IBKR gateway."""

from __future__ import annotations

from typing import Any

import requests
import urllib3


def suppress_local_tls_warnings() -> None:
    """Hide warnings for the gateway's local self-signed certificate."""

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class GatewayClient:
    """Small wrapper around requests.Session for gateway-local JSON calls."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 15,
        verify_tls: bool = False,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.verify = verify_tls

    def request_json(self, method: str, path: str, *, json_body: object | None = None) -> Any:
        response = self.session.request(
            method,
            f"{self.base_url}{path}",
            json=json_body,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def get_json(self, path: str) -> dict[str, Any]:
        payload = self.request_json("GET", path)
        return payload if isinstance(payload, dict) else {}

    def post_json(self, path: str, json_body: object | None = None) -> dict[str, Any]:
        payload = self.request_json("POST", path, json_body={} if json_body is None else json_body)
        return payload if isinstance(payload, dict) else {}
