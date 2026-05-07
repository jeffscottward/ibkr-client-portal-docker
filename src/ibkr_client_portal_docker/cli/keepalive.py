"""CLI for keeping an authenticated gateway session active."""

from __future__ import annotations

import argparse
import sys

from ibkr_client_portal_docker.client import GatewayClient, suppress_local_tls_warnings
from ibkr_client_portal_docker.config import DEFAULT_API_BASE_URL
from ibkr_client_portal_docker.keepalive import run_keepalive


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_API_BASE_URL)
    parser.add_argument("--interval", type=int, default=60)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    suppress_local_tls_warnings()
    client = GatewayClient(args.base_url)

    try:
        return run_keepalive(
            client,
            interval_seconds=args.interval,
            once=args.once,
            on_message=lambda message: print(message, flush=True),
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
