# Contributing

## Branching

- `main` is the release branch.
- Use short feature branches, for example `feat/add-health-check` or `fix/redaction-key`.
- Pull requests should stay focused and include validation output.

## Versioning

This project follows semantic versioning:

- `PATCH`: docs, CI, tests, or backward-compatible fixes.
- `MINOR`: new commands, new smoke checks, or backward-compatible workflow improvements.
- `MAJOR`: changes that alter the default gateway behavior, command names, or expected local setup.

## Release Process

1. Update `CHANGELOG.md`.
2. Update `pyproject.toml` version.
3. Run validation:

   ```bash
   uv run pytest
   bash -n start.sh
   docker compose config --quiet
   docker compose build
   ```

4. Tag the release:

   ```bash
   git tag v0.1.0
   git push origin main --tags
   ```

5. Create the GitHub release from the tag and changelog notes.

## Testing Strategy

- Unit tests cover local code that can be tested without IBKR credentials.
- CI builds the Docker image to catch broken base images or gateway download changes.
- Live gateway authentication cannot run in public CI because it requires browser login and 2FA.
- Run `./start.sh` locally for the end-to-end smoke test.

## Security

- Never paste raw IBKR gateway output into issues or pull requests.
- Redact tokens, session IDs, usernames, account IDs, IP addresses, and hardware identifiers.
- Use paper trading first. Authenticated live sessions can access real brokerage data and trading endpoints.
