# Security Policy

## Sensitive Data

Do not publish:

- IBKR usernames or credentials
- account IDs or account aliases
- session tokens or gateway cookies
- IP addresses from gateway responses
- hardware identifiers or MAC addresses
- raw logs from authenticated gateway sessions

`scripts/read_only_check.py` and `ibkr-read-only-check` redact common sensitive fields, but review output before sharing it.

## Supported Versions

Only the latest `main` branch is actively maintained until formal releases begin.

## Reporting Issues

For security-sensitive reports, avoid public issues. Contact the repository owner directly through GitHub.
