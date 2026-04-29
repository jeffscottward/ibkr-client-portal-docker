from __future__ import annotations

from ibkr_client_portal_docker.client import GatewayClient


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self):
        self.verify = True
        self.calls = []

    def request(self, method: str, url: str, json=None, timeout=None):
        self.calls.append({"method": method, "url": url, "json": json, "timeout": timeout})
        return FakeResponse({"ok": True})


def test_gateway_client_normalizes_base_url_and_disables_tls_by_default() -> None:
    session = FakeSession()

    client = GatewayClient("https://localhost:5000/v1/api/", session=session)
    payload = client.request_json("GET", "/sso/validate")

    assert payload == {"ok": True}
    assert session.verify is False
    assert session.calls == [
        {
            "method": "GET",
            "url": "https://localhost:5000/v1/api/sso/validate",
            "json": None,
            "timeout": 15,
        }
    ]


def test_gateway_client_post_json_sends_empty_body_by_default() -> None:
    session = FakeSession()
    client = GatewayClient("https://localhost:5000/v1/api", session=session)

    assert client.post_json("/iserver/auth/status") == {"ok": True}
    assert session.calls[0]["json"] == {}
