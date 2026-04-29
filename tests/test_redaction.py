from ibkr_client_portal_docker.redaction import REDACTED, redact_sensitive


def test_redact_sensitive_redacts_nested_ibkr_identifiers() -> None:
    payload = {
        "USER_NAME": "person",
        "TOKEN": "secret",
        "portfolio": [
            {
                "accountId": "U123",
                "displayName": "U123",
                "currency": "USD",
            }
        ],
        "authStatus": {"authenticated": True, "MAC": "00:11"},
    }

    assert redact_sensitive(payload) == {
        "USER_NAME": REDACTED,
        "TOKEN": REDACTED,
        "portfolio": [
            {
                "accountId": REDACTED,
                "displayName": REDACTED,
                "currency": "USD",
            }
        ],
        "authStatus": {"authenticated": True, "MAC": REDACTED},
    }


def test_redact_sensitive_preserves_operational_booleans() -> None:
    payload = {"authenticated": True, "connected": True, "type": "INDIVIDUAL"}

    assert redact_sensitive(payload) == payload
