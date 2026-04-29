# Changelog

All notable changes to this project are documented here.

This project uses semantic versioning. Public releases are tagged as `vMAJOR.MINOR.PATCH`.

## Unreleased

- Refactored gateway checks into an importable Python package.
- Added unit tests for redaction, endpoint contracts, and authentication readiness.
- Added GitHub Actions CI for Python tests, shell syntax, Compose validation, and gateway image builds.
- Added public release and contribution documentation.

## 0.1.0

- Initial Dockerized IBKR Client Portal Gateway setup.
- Added authenticated read-only smoke checks.
- Defaulted to IBKR Beta gateway after local Standard gateway authentication failures.
