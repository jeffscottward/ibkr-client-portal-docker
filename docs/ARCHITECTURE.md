# Architecture

## Goals

- Keep Docker and shell orchestration simple.
- Keep IBKR HTTP behavior testable without live credentials.
- Make read-only smoke checks explicit and easy to extend.
- Avoid logging sensitive account/session details by default.

## Components

- `Dockerfile`: builds a local Client Portal Gateway image from IBKR's gateway zip and installs maintained standard/beta runtime configs.
- `docker-compose.yaml`: exposes the gateway only on loopback.
- `start.sh`: starts Docker Compose under PM2, opens the browser, waits for authentication, then runs read-only checks.
- `conf.beta.yaml`: optional diagnostic runtime config for IBKR's beta backend, with Docker-safe loopback/private-network allowlist entries.
- `src/ibkr_client_portal_docker/client.py`: gateway-local HTTP client.
- `src/ibkr_client_portal_docker/readiness.py`: gateway and brokerage-session readiness logic.
- `src/ibkr_client_portal_docker/smoke.py`: read-only endpoint checks.
- `src/ibkr_client_portal_docker/redaction.py`: recursive output redaction.
- `scripts/*.py`: compatibility wrappers around packaged CLIs.

## External Boundaries

- IBKR gateway zip download.
- Docker base image.
- Local browser login and 2FA.
- IBKR Client Portal Web API endpoints.
- IBKR standard and beta gateway backends.

## Stability Approach

- Unit tests cover local behavior and endpoint contracts.
- CI builds the Docker image to catch gateway download or base-image breakage.
- A weekly scheduled CI run catches external drift even when the repo is idle.
- Live authentication remains a local manual smoke test because IBKR requires browser login and 2FA.
