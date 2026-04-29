from __future__ import annotations

import requests

from ibkr_client_portal_docker.readiness import (
    describe_brokerage_readiness,
    wait_for_brokerage_auth,
    wait_for_gateway,
)


class FakeClient:
    def __init__(self, *, post_payload=None, get_payload=None, post_error=None, get_error=None):
        self.post_payload = post_payload
        self.get_payload = get_payload
        self.post_error = post_error
        self.get_error = get_error

    def post_json(self, path: str, json_body: object | None = None):
        assert path == "/iserver/auth/status"
        if self.post_error:
            raise self.post_error
        return self.post_payload

    def get_json(self, path: str):
        assert path == "/sso/validate"
        if self.get_error:
            raise self.get_error
        return self.get_payload


def test_describe_brokerage_ready_when_authenticated_true() -> None:
    ready, message = describe_brokerage_readiness(FakeClient(post_payload={"authenticated": True}))

    assert ready is True
    assert message == "brokerage session authenticated"


def test_describe_brokerage_pending_when_auth_connected_false() -> None:
    ready, message = describe_brokerage_readiness(
        FakeClient(post_payload={"authenticated": False, "connected": False})
    )

    assert ready is False
    assert message == "brokerage auth pending; connected=False"


def test_describe_brokerage_reports_sso_valid_when_auth_endpoint_unauthorized() -> None:
    ready, message = describe_brokerage_readiness(
        FakeClient(post_error=requests.HTTPError("401"), get_payload={"RESULT": True})
    )

    assert ready is False
    assert message == "SSO valid; waiting for brokerage auth"


def test_wait_for_brokerage_auth_returns_true_without_sleeping_when_ready() -> None:
    messages: list[str] = []

    ok = wait_for_brokerage_auth(
        FakeClient(post_payload={"authenticated": True}),
        timeout_seconds=10,
        interval_seconds=5,
        on_message=messages.append,
        sleep=lambda _: (_ for _ in ()).throw(AssertionError("sleep should not run")),
    )

    assert ok is True
    assert messages == ["brokerage session authenticated"]


class FakeGatewayResponse:
    status_code = 200


class FakeGatewaySession:
    verify = False

    def __init__(self, *, failures_before_success: int):
        self.failures_before_success = failures_before_success
        self.calls = 0

    def get(self, url: str, timeout: float, allow_redirects: bool):
        assert url == "https://localhost:5000/"
        assert timeout == 10
        assert allow_redirects is False
        self.calls += 1
        if self.calls <= self.failures_before_success:
            raise requests.Timeout("not ready")
        return FakeGatewayResponse()


def test_wait_for_gateway_reports_transition_to_reachable() -> None:
    messages: list[str] = []

    ok = wait_for_gateway(
        FakeGatewaySession(failures_before_success=1),
        url="https://localhost:5000/",
        timeout_seconds=10,
        interval_seconds=1,
        on_message=messages.append,
        sleep=lambda _: None,
        monotonic=iter([0, 1, 2]).__next__,
    )

    assert ok is True
    assert messages == ["Gateway not ready: Timeout", "Gateway reachable: HTTP 200"]


def test_wait_for_gateway_treats_login_redirect_as_reachable() -> None:
    messages: list[str] = []
    response = FakeGatewayResponse()
    response.status_code = 302

    class RedirectGatewaySession:
        verify = False

        def get(self, url: str, timeout: float, allow_redirects: bool):
            assert allow_redirects is False
            return response

    ok = wait_for_gateway(
        RedirectGatewaySession(),
        url="https://localhost:5000/",
        timeout_seconds=10,
        interval_seconds=1,
        on_message=messages.append,
        sleep=lambda _: (_ for _ in ()).throw(AssertionError("sleep should not run")),
    )

    assert ok is True
    assert messages == ["Gateway reachable: HTTP 302"]
