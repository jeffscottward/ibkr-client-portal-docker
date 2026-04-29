from __future__ import annotations

import requests

from ibkr_client_portal_docker.config import Endpoint
from ibkr_client_portal_docker.smoke import run_smoke_checks


class FakeJsonClient:
    def request_json(self, method: str, path: str, *, json_body: object | None = None):
        assert method == "GET"
        assert path == "/portfolio/accounts"
        assert json_body is None
        return [{"accountId": "U123", "type": "INDIVIDUAL"}]


def test_run_smoke_checks_redacts_success_payloads() -> None:
    results = run_smoke_checks(FakeJsonClient(), (Endpoint("portfolio_accounts", "GET", "/portfolio/accounts"),))

    assert len(results) == 1
    assert results[0].ok is True
    assert results[0].payload == [{"accountId": "[REDACTED]", "type": "INDIVIDUAL"}]


class FakeHttpErrorResponse:
    status_code = 401
    text = "unauthorized"


class FakeFailingJsonClient:
    def __init__(self, error: requests.RequestException):
        self.error = error

    def request_json(self, method: str, path: str, *, json_body: object | None = None):
        raise self.error


def test_run_smoke_checks_reports_http_errors() -> None:
    error = requests.HTTPError("unauthorized")
    error.response = FakeHttpErrorResponse()

    results = run_smoke_checks(FakeFailingJsonClient(error), (Endpoint("auth_status", "POST", "/x"),))

    assert results[0].ok is False
    assert results[0].status_code == 401
    assert results[0].error == "unauthorized"


def test_run_smoke_checks_reports_request_errors() -> None:
    results = run_smoke_checks(
        FakeFailingJsonClient(requests.Timeout("timed out")),
        (Endpoint("auth_status", "POST", "/x"),),
    )

    assert results[0].ok is False
    assert results[0].status_code is None
    assert results[0].error == "timed out"
