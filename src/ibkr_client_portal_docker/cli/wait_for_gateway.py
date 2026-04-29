"""CLI for waiting until the local gateway accepts HTTPS requests."""

from __future__ import annotations

import argparse

import requests

from ibkr_client_portal_docker.client import suppress_local_tls_warnings
from ibkr_client_portal_docker.config import DEFAULT_LOGIN_URL
from ibkr_client_portal_docker.readiness import wait_for_gateway


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=DEFAULT_LOGIN_URL)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--interval", type=int, default=3)
    args = parser.parse_args()

    suppress_local_tls_warnings()
    session = requests.Session()
    session.verify = False

    return 0 if wait_for_gateway(
        session,
        url=args.url,
        timeout_seconds=args.timeout,
        interval_seconds=args.interval,
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
