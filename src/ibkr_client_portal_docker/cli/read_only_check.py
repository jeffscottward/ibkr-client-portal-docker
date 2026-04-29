"""CLI for read-only authenticated gateway checks."""

from __future__ import annotations

import argparse
import json

from ibkr_client_portal_docker.client import GatewayClient, suppress_local_tls_warnings
from ibkr_client_portal_docker.config import DEFAULT_API_BASE_URL
from ibkr_client_portal_docker.smoke import run_smoke_checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_API_BASE_URL)
    args = parser.parse_args()

    suppress_local_tls_warnings()
    client = GatewayClient(args.base_url)

    for result in run_smoke_checks(client):
        print(f"\n## {result.name}")
        if result.ok:
            print(json.dumps(result.payload, indent=2, sort_keys=True))
        elif result.status_code is not None:
            print(f"HTTP {result.status_code}: {result.error}")
        else:
            print(f"Request failed: {result.error}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
