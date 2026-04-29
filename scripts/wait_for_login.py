#!/usr/bin/env python3
"""Compatibility wrapper for the packaged login wait CLI."""

from __future__ import annotations

from ibkr_client_portal_docker.cli.wait_for_login import main


if __name__ == "__main__":
    raise SystemExit(main())
