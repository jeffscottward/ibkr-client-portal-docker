from __future__ import annotations

import re

import pytest
import requests

from ibkr_client_portal_docker.keepalive import run_keepalive, tickle_gateway


class FakeClient:
    def __init__(self, payload=None, error=None):
        self.payload = payload
        self.error = error
        self.paths = []

    def get_json(self, path: str):
        self.paths.append(path)
        if self.error:
            raise self.error
        return self.payload


def test_tickle_gateway_reports_authenticated_session_without_sensitive_payload() -> None:
    result = tickle_gateway(
        FakeClient(
            {
                "session": "secret-session",
                "userId": "secret-user",
                "ssoExpires": 500000,
                "iserver": {"authStatus": {"authenticated": True, "connected": True, "MAC": "00:11"}},
            }
        )
    )

    assert result.ok is True
    assert result.message == "tickle ok; authenticated=True; connected=True; ssoExpires=500000"
    assert "secret" not in result.message
    assert "00:11" not in result.message


def test_tickle_gateway_reports_unauthenticated_session() -> None:
    result = tickle_gateway(FakeClient({"iserver": {"authStatus": {"authenticated": False, "connected": True}}}))

    assert result.ok is False
    assert result.message == "tickle ok; authenticated=False; connected=True; ssoExpires=None"


def test_tickle_gateway_reports_http_status_without_response_body() -> None:
    response = requests.Response()
    response.status_code = 401
    error = requests.HTTPError("unauthorized", response=response)

    result = tickle_gateway(FakeClient(error=error))

    assert result.ok is False
    assert result.message == "tickle failed: HTTP 401"


def test_run_keepalive_once_returns_success_and_timestamps_message() -> None:
    messages: list[str] = []

    code = run_keepalive(
        FakeClient({"iserver": {"authStatus": {"authenticated": True, "connected": True}}}),
        interval_seconds=60,
        once=True,
        on_message=messages.append,
        sleep=lambda _: (_ for _ in ()).throw(AssertionError("sleep should not run")),
    )

    assert code == 0
    assert re.match(r"^\d{4}-\d{2}-\d{2}T.* tickle ok; authenticated=True", messages[0])


def test_run_keepalive_rejects_invalid_interval() -> None:
    with pytest.raises(ValueError, match="interval_seconds"):
        run_keepalive(FakeClient(), interval_seconds=0, once=True)
