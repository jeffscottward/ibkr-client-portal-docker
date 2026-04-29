"""CLI for waiting until brokerage authentication is available."""

from __future__ import annotations

import argparse

from ibkr_client_portal_docker.client import GatewayClient, suppress_local_tls_warnings
from ibkr_client_portal_docker.config import DEFAULT_API_BASE_URL
from ibkr_client_portal_docker.readiness import wait_for_brokerage_auth


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_API_BASE_URL)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--interval", type=int, default=5)
    args = parser.parse_args()

    suppress_local_tls_warnings()
    client = GatewayClient(args.base_url)

    return 0 if wait_for_brokerage_auth(
        client,
        timeout_seconds=args.timeout,
        interval_seconds=args.interval,
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
