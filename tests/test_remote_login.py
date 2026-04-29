from __future__ import annotations

import pytest

from ibkr_client_portal_docker.remote_login import (
    PASSWORD_SELECTORS,
    USERNAME_SELECTORS,
    RemoteDesktopConfig,
    RemoteLoginError,
    fill_login_form,
    find_command,
    is_loopback_host,
    is_loopback_url,
    validate_desktop_config,
    validate_loopback_url,
)


class FakeLocator:
    def __init__(self, selector: str, visible: bool):
        self.selector = selector
        self.visible = visible
        self.filled = None
        self.clicked = False

    @property
    def first(self):
        return self

    def wait_for(self, state: str, timeout: int):
        if not self.visible:
            raise RuntimeError(f"{self.selector} not visible")

    def fill(self, value: str):
        self.filled = value

    def click(self):
        self.clicked = True


class FakePage:
    def __init__(self):
        self.goto_args = None
        self.locators = {
            USERNAME_SELECTORS[0]: FakeLocator(USERNAME_SELECTORS[0], True),
            PASSWORD_SELECTORS[0]: FakeLocator(PASSWORD_SELECTORS[0], True),
            'button[type="submit"]': FakeLocator('button[type="submit"]', True),
        }

    def goto(self, url: str, wait_until: str, timeout: float):
        self.goto_args = (url, wait_until, timeout)

    def locator(self, selector: str):
        return self.locators.get(selector, FakeLocator(selector, False))


def test_fill_login_form_fills_credentials_and_clicks_submit() -> None:
    page = FakePage()

    fill_login_form(page, login_url="https://localhost:5000/", username="user", password="password")

    assert page.goto_args == ("https://localhost:5000/", "domcontentloaded", 60000)
    assert page.locators[USERNAME_SELECTORS[0]].filled == "user"
    assert page.locators[PASSWORD_SELECTORS[0]].filled == "password"
    assert page.locators['button[type="submit"]'].clicked is True


def test_fill_login_form_raises_when_username_missing() -> None:
    page = FakePage()
    page.locators[USERNAME_SELECTORS[0]].visible = False

    with pytest.raises(RemoteLoginError, match="username"):
        fill_login_form(page, login_url="https://localhost:5000/", username="user", password="password")


def test_remote_desktop_config_exposes_loopback_novnc_url() -> None:
    config = RemoteDesktopConfig(novnc_host="127.0.0.1", novnc_port=6080)

    assert config.novnc_url == "http://127.0.0.1:6080/vnc.html"


@pytest.mark.parametrize("host", ["127.0.0.1", "::1", "localhost"])
def test_loopback_hosts_are_allowed(host: str) -> None:
    assert is_loopback_host(host) is True


@pytest.mark.parametrize(
    "url",
    [
        "https://localhost:5000/",
        "https://127.0.0.1:5000/v1/api",
        "http://[::1]:6080/vnc.html",
    ],
)
def test_loopback_urls_are_allowed(url: str) -> None:
    assert is_loopback_url(url) is True


def test_loopback_url_validation_rejects_external_hosts() -> None:
    with pytest.raises(RemoteLoginError, match="loopback"):
        validate_loopback_url("https://example.com/", "login URL")


def test_remote_desktop_config_rejects_public_novnc_host() -> None:
    config = RemoteDesktopConfig(novnc_host="0.0.0.0", novnc_port=6080)

    with pytest.raises(RemoteLoginError, match="loopback"):
        validate_desktop_config(config)


def test_remote_desktop_config_allows_public_host_when_novnc_disabled() -> None:
    config = RemoteDesktopConfig(novnc_host="0.0.0.0", no_novnc=True)

    validate_desktop_config(config)


def test_find_command_returns_first_available_command(monkeypatch) -> None:
    monkeypatch.setattr("ibkr_client_portal_docker.remote_login.shutil.which", lambda name: "/bin/echo" if name == "echo" else None)

    assert find_command("missing", "echo") == "/bin/echo"


def test_find_command_raises_when_missing(monkeypatch) -> None:
    monkeypatch.setattr("ibkr_client_portal_docker.remote_login.shutil.which", lambda name: None)

    with pytest.raises(RemoteLoginError, match="missing"):
        find_command("missing")
