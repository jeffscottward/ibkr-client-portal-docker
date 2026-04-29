"""CLI for assisted remote IBKR browser login."""

from __future__ import annotations

import argparse
import getpass
import shutil
import sys

from playwright.sync_api import sync_playwright

from ibkr_client_portal_docker.client import GatewayClient, suppress_local_tls_warnings
from ibkr_client_portal_docker.config import DEFAULT_API_BASE_URL, DEFAULT_LOGIN_URL
from ibkr_client_portal_docker.readiness import wait_for_brokerage_auth
from ibkr_client_portal_docker.remote_login import (
    RemoteDesktopConfig,
    RemoteLoginError,
    fill_login_form,
    remote_desktop,
    validate_desktop_config,
    validate_loopback_url,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--login-url", default=DEFAULT_LOGIN_URL)
    parser.add_argument("--base-url", default=DEFAULT_API_BASE_URL)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--interval", type=int, default=5)
    parser.add_argument("--display", default=":99")
    parser.add_argument("--novnc-host", default="127.0.0.1")
    parser.add_argument("--novnc-port", type=int, default=6080)
    parser.add_argument("--vnc-port", type=int, default=5900)
    parser.add_argument("--no-novnc", action="store_true")
    args = parser.parse_args()

    desktop_config = RemoteDesktopConfig(
        display=args.display,
        novnc_host=args.novnc_host,
        novnc_port=args.novnc_port,
        vnc_port=args.vnc_port,
        no_novnc=args.no_novnc,
    )
    try:
        validate_loopback_url(args.login_url, "login URL")
        validate_loopback_url(args.base_url, "base URL")
        validate_desktop_config(desktop_config)

        username = input("IBKR username: ")
        password = getpass.getpass("IBKR password: ")

        suppress_local_tls_warnings()

        if not args.no_novnc:
            print(f"Remote browser available through SSH tunnel at {desktop_config.novnc_url}")
            print("Approve IBKR 2FA manually when prompted. This tool does not bypass 2FA.")

        chromium_path = shutil.which("chromium") or shutil.which("chromium-browser")
        launch_kwargs = {
            "headless": False,
            "args": ["--ignore-certificate-errors", "--no-sandbox"],
        }
        if chromium_path:
            launch_kwargs["executable_path"] = chromium_path

        with remote_desktop(desktop_config):
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(**launch_kwargs)
                try:
                    context = browser.new_context(ignore_https_errors=True)
                    page = context.new_page()
                    fill_login_form(page, login_url=args.login_url, username=username, password=password)

                    client = GatewayClient(args.base_url)
                    ok = wait_for_brokerage_auth(
                        client,
                        timeout_seconds=args.timeout,
                        interval_seconds=args.interval,
                    )
                finally:
                    browser.close()
    except RemoteLoginError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
