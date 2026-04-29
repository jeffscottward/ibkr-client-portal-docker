from ibkr_client_portal_docker.config import DEFAULT_GATEWAY_ZIP_URL, SMOKE_CHECKS


def test_default_gateway_uses_beta_zip() -> None:
    assert DEFAULT_GATEWAY_ZIP_URL.endswith("clientportal.beta.gw.zip")


def test_smoke_check_contract_tracks_ibkr_read_only_endpoints() -> None:
    assert [(check.name, check.method, check.path) for check in SMOKE_CHECKS] == [
        ("sso_validate", "GET", "/sso/validate"),
        ("auth_status", "POST", "/iserver/auth/status"),
        ("tickle", "GET", "/tickle"),
        ("portfolio_accounts", "GET", "/portfolio/accounts"),
    ]
