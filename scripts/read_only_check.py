#!/usr/bin/env python3
"""Compatibility wrapper for the packaged read-only check CLI."""

from __future__ import annotations

from ibkr_client_portal_docker.cli.read_only_check import main


if __name__ == "__main__":
    raise SystemExit(main())
