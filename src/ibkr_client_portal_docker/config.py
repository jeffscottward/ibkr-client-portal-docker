"""Project defaults for the local IBKR Client Portal Gateway."""

from __future__ import annotations

from dataclasses import dataclass


DEFAULT_LOGIN_URL = "https://localhost:5000/"
DEFAULT_API_BASE_URL = "https://localhost:5000/v1/api"
DEFAULT_GATEWAY_ZIP_URL = "https://download2.interactivebrokers.com/portal/clientportal.beta.gw.zip"
DEFAULT_NOVNC_URL = "http://127.0.0.1:6080/vnc.html"


@dataclass(frozen=True)
class Endpoint:
    name: str
    method: str
    path: str


SMOKE_CHECKS: tuple[Endpoint, ...] = (
    Endpoint("sso_validate", "GET", "/sso/validate"),
    Endpoint("auth_status", "POST", "/iserver/auth/status"),
    Endpoint("tickle", "GET", "/tickle"),
    Endpoint("portfolio_accounts", "GET", "/portfolio/accounts"),
)
