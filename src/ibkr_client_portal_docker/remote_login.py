"""Assisted browser login helpers for a remote Linux gateway host."""

from __future__ import annotations

import os
import shutil
import subprocess
import time
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from ipaddress import ip_address
from typing import Protocol
from urllib.parse import urlparse


USERNAME_SELECTORS = (
    'input[name="username"]',
    'input[name="user_name"]',
    'input[id*="user" i]',
    'input[autocomplete="username"]',
    'input[type="text"]',
)
PASSWORD_SELECTORS = (
    'input[name="password"]',
    'input[id*="pass" i]',
    'input[autocomplete="current-password"]',
    'input[type="password"]',
)
SUBMIT_SELECTORS = (
    'button[type="submit"]',
    'input[type="submit"]',
    'button:has-text("Log In")',
    'button:has-text("Login")',
    'text=Log In',
    'text=Login',
)


class BrowserPage(Protocol):
    def goto(self, url: str, wait_until: str, timeout: float) -> object: ...

    def locator(self, selector: str) -> object: ...


@dataclass(frozen=True)
class RemoteDesktopConfig:
    display: str = ":99"
    novnc_host: str = "127.0.0.1"
    novnc_port: int = 6080
    vnc_port: int = 5900
    no_novnc: bool = False

    @property
    def novnc_url(self) -> str:
        return f"http://{self.novnc_host}:{self.novnc_port}/vnc.html"


class RemoteLoginError(RuntimeError):
    """Raised when the assisted browser login flow cannot continue."""


def is_loopback_host(host: str) -> bool:
    if host == "localhost":
        return True

    try:
        return ip_address(host).is_loopback
    except ValueError:
        return False


def is_loopback_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and parsed.hostname is not None and is_loopback_host(parsed.hostname)


def validate_loopback_url(url: str, label: str) -> None:
    if not is_loopback_url(url):
        raise RemoteLoginError(f"{label} must be an http(s) URL on localhost or another loopback host")


def validate_desktop_config(config: RemoteDesktopConfig) -> None:
    if not config.no_novnc and not is_loopback_host(config.novnc_host):
        raise RemoteLoginError("noVNC must bind to a loopback host such as 127.0.0.1 or localhost")


def find_command(*names: str) -> str:
    for name in names:
        path = shutil.which(name)
        if path:
            return path
    raise RemoteLoginError(f"Missing required command: {' or '.join(names)}")


def fill_first_visible(page: BrowserPage, selectors: Sequence[str], value: str, label: str) -> str:
    last_error = ""
    for selector in selectors:
        locator = page.locator(selector).first
        try:
            locator.wait_for(state="visible", timeout=3000)
            locator.fill(value)
            return selector
        except Exception as exc:
            last_error = str(exc)

    raise RemoteLoginError(f"Could not find visible {label} field. Last error: {last_error}")


def click_first_visible(page: BrowserPage, selectors: Sequence[str], label: str) -> str:
    last_error = ""
    for selector in selectors:
        locator = page.locator(selector).first
        try:
            locator.wait_for(state="visible", timeout=3000)
            locator.click()
            return selector
        except Exception as exc:
            last_error = str(exc)

    raise RemoteLoginError(f"Could not find visible {label} control. Last error: {last_error}")


def fill_login_form(page: BrowserPage, *, login_url: str, username: str, password: str) -> None:
    page.goto(login_url, wait_until="domcontentloaded", timeout=60000)
    fill_first_visible(page, USERNAME_SELECTORS, username, "username")
    fill_first_visible(page, PASSWORD_SELECTORS, password, "password")
    click_first_visible(page, SUBMIT_SELECTORS, "login submit")


def _start_process(command: Sequence[str], *, env: dict[str, str] | None = None) -> subprocess.Popen[bytes]:  # pragma: no cover
    return subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env,
    )


@contextmanager
def remote_desktop(config: RemoteDesktopConfig) -> Iterator[None]:  # pragma: no cover
    """Start an ephemeral Xvfb/noVNC desktop bound to loopback."""

    validate_desktop_config(config)
    processes: list[subprocess.Popen[bytes]] = []
    env = os.environ.copy()
    previous_display = os.environ.get("DISPLAY")
    env["DISPLAY"] = config.display

    try:
        xvfb = find_command("Xvfb")
        processes.append(_start_process([xvfb, config.display, "-screen", "0", "1280x900x24"], env=env))
        time.sleep(1)

        openbox = shutil.which("openbox")
        if openbox:
            processes.append(_start_process([openbox], env=env))

        if not config.no_novnc:
            x11vnc = find_command("x11vnc")
            processes.append(
                _start_process(
                    [
                        x11vnc,
                        "-display",
                        config.display,
                        "-rfbport",
                        str(config.vnc_port),
                        "-localhost",
                        "-forever",
                        "-shared",
                        "-nopw",
                    ],
                    env=env,
                )
            )

            websockify = find_command("websockify")
            processes.append(
                _start_process(
                    [
                        websockify,
                        "--web=/usr/share/novnc",
                        f"{config.novnc_host}:{config.novnc_port}",
                        f"127.0.0.1:{config.vnc_port}",
                    ],
                    env=env,
                )
            )

        os.environ["DISPLAY"] = config.display
        yield
    finally:
        if previous_display is None:
            os.environ.pop("DISPLAY", None)
        else:
            os.environ["DISPLAY"] = previous_display

        for process in reversed(processes):
            process.terminate()
        for process in reversed(processes):
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
