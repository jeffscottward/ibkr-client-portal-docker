# ibkr-vertex-ai-fund

Local Docker baseline for the Interactive Brokers Client Portal Gateway.

This starts from the OSQuant/blog `ibportal` pattern:

- download IBKR's `clientportal.gw.zip`
- copy `conf.yaml` into `root/conf.yaml`
- expose the gateway on port `5000`
- run `bin/run.sh root/conf.yaml`
- use Python `requests` with TLS verification disabled for the gateway's self-signed local cert

Current IBKR doc updates applied here:

- uses IBKR's current Standard Release gateway URL
- uses a maintained multi-arch Java 8 JRE image instead of the old `openjdk:8u212-jre-alpine3.9`
- keeps `listenPort: 5000`, which IBKR documents as the default
- adds `ccp: false`, matching current IBKR `conf.yaml` examples
- binds Docker to `127.0.0.1:5000` so the login UI is not exposed on the LAN

## Requirements

- Docker with Docker Compose
- active, funded IBKR Pro account
- supported IBKR 2FA method
- browser login on the same machine running this gateway

Use paper trading first. After live login, authenticated API calls can place real orders.

## Run

```bash
./start.sh
```

`start.sh` starts the Docker Compose gateway under PM2, waits for the local gateway to accept HTTPS requests, opens `https://localhost:5000/`, waits until IBKR reports the brokerage session as authenticated, then runs `scripts/read_only_check.py`.

The working Beta gateway path is also preserved as:

```bash
./start-beta.sh
```

If the browser does not open automatically, open:

```text
https://localhost:5000/
```

Your browser will warn about a local self-signed certificate. Continue only for this local gateway, then log in to IBKR and approve 2FA.

## Read-only checks

If the gateway is already running and you only want to run the checks:

```bash
uv run scripts/read_only_check.py
```

The script calls only read/session endpoints:

- `/sso/validate`
- `/iserver/auth/status`
- `/tickle`
- `/portfolio/accounts`

Sensitive token, user, account, session, IP, and hardware fields are redacted before output.

## Blog baseline example

After login:

```bash
uv run examples/aapl_contract_info.py
```

This mirrors the blog's AAPL contract metadata example against `https://localhost:5000/v1/api`.

## Notes

IBKR documents the Client Portal Gateway as local-machine software. Keep the browser login, gateway, and API client on this machine unless moving to a separately approved OAuth flow.

If the browser shows `Client login succeeds` but API calls still return `401 Unauthorized`, the login callback completed but the gateway did not expose an authenticated API session. Restart the gateway and retry at exactly `https://localhost:5000/`. IBKR also publishes a Beta gateway for Standard gateway issues:

```bash
IBKR_GATEWAY_ZIP_URL=https://download2.interactivebrokers.com/portal/clientportal.beta.gw.zip ./start.sh
```

Stop the gateway with:

```bash
pm2 stop ibkr-vertex-ai-fund-gateway
pm2 delete ibkr-vertex-ai-fund-gateway
docker compose down
```
