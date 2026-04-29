#!/usr/bin/env python3
"""Wait until the local IBKR gateway accepts HTTPS requests."""

from __future__ import annotations

import argparse
import sys
import time

import requests
import urllib3


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="https://localhost:5000/")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--interval", type=int, default=3)
    args = parser.parse_args()

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    session = requests.Session()
    session.verify = False

    deadline = time.monotonic() + args.timeout
    last_message = ""

    while time.monotonic() < deadline:
        try:
            response = session.get(args.url, timeout=10)
            print(f"Gateway reachable: HTTP {response.status_code}")
            return 0
        except requests.RequestException as exc:
            message = f"Gateway not ready: {exc.__class__.__name__}"
            if message != last_message:
                print(message)
                last_message = message

        time.sleep(args.interval)

    print(f"Timed out after {args.timeout}s waiting for gateway", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
