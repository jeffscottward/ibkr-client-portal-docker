<div align="center">
  <p>
    <img src="https://img.shields.io/badge/Interactive%20Brokers-Client%20Portal-cc0000?style=for-the-badge&logo=interactivebrokers&logoColor=white" alt="Interactive Brokers Client Portal" />
    <span>&nbsp;+&nbsp;</span>
    <img src="https://img.shields.io/badge/Docker-Gateway-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker Gateway" />
  </p>

  <h1>ibkr-client-portal-docker</h1>
  <p><strong>Dockerized IBKR Client Portal Gateway with authenticated read-only smoke checks.</strong></p>
  <p>
    <a href="https://github.com/jeffscottward/ibkr-client-portal-docker/actions/workflows/ci.yml"><img src="https://github.com/jeffscottward/ibkr-client-portal-docker/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
    <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT License" />
    <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python 3.10+" />
  </p>
</div>

Local Docker baseline for the Interactive Brokers Client Portal Gateway.

This starts from the OSQuant/blog `ibportal` pattern:

- download IBKR's `clientportal.gw.zip`
- copy `conf.yaml` into `root/conf.yaml`
- expose the gateway on port `5000`
- run `bin/run.sh root/conf.yaml`
- use Python `requests` with TLS verification disabled for the gateway's self-signed local cert

Current IBKR doc updates applied here:

- uses IBKR's Beta Release gateway URL by default because it authenticated successfully while the Standard Release did not in local testing
- uses a maintained multi-arch Java 8 JRE image instead of the old `openjdk:8u212-jre-alpine3.9`
- keeps `listenPort: 5000`, which IBKR documents as the default
- adds `ccp: false`, matching current IBKR `conf.yaml` examples
- binds Docker to IPv4 and IPv6 loopback so the login UI is not exposed on the LAN

## Assumptions and dependencies

This repo is intentionally small, but it assumes a few local tools and account conditions.

Local tools:

- Docker with Docker Compose v2
- PM2, used to keep the gateway process running outside the current shell
- `uv`, used to run the Python smoke-check scripts and manage their dependencies
- a desktop browser on the same machine as Docker
- macOS `open` or Linux `xdg-open` if you want `start.sh` to open the login page automatically

Install examples:

```bash
npm install -g pm2
curl -LsSf https://astral.sh/uv/install.sh | sh
```

IBKR/account assumptions:

- active IBKR account with Client Portal API access
- IBKR Pro account for protected Client Portal Web API endpoints
- supported 2FA method, such as IB Key
- browser login, gateway, and API client all on the same machine

Runtime assumptions:

- the gateway binds to `https://localhost:5000/`
- Docker exposes only local loopback ports, not the LAN
- the gateway uses a local self-signed certificate, so browser and Python checks disable or bypass TLS verification for localhost only
- the default gateway download is IBKR's Beta Release because it authenticated successfully in local testing while the Standard Release did not

Use paper trading first. After live login, authenticated API calls can place real orders.

## Run

```bash
./start.sh
```

`start.sh` starts the Docker Compose gateway under PM2, waits for the local gateway to accept HTTPS requests, opens `https://localhost:5000/`, waits until IBKR reports the brokerage session as authenticated, then runs `scripts/read_only_check.py`.

If the browser does not open automatically, open:

```text
https://localhost:5000/
```

Your browser will warn about a local self-signed certificate. Continue only for this local gateway, then log in to IBKR and approve 2FA.

## Read-only checks

If the gateway is already running and you only want to run the checks:

```bash
uv run ibkr-read-only-check
```

The script calls only read/session endpoints:

- `/sso/validate`
- `/iserver/auth/status`
- `/tickle`
- `/portfolio/accounts`

Sensitive token, user, account, session, IP, and hardware fields are redacted before output.

## Development checks

Local checks:

```bash
uv run pytest
bash -n start.sh
docker compose config --quiet
docker compose build
```

CI runs unit tests, enforces 80% package coverage, validates Compose config, and builds the gateway image. A weekly scheduled CI run helps catch external drift in Docker base images or IBKR's gateway download.

## Remote Kali VPS mode

This repo can prepare an already-provisioned Kali Linux VPS to act as a private IBKR gateway host. It does not create the VPS or install Kali itself.

The remote mode uses `systemd`, Docker, Chromium, Xvfb, x11vnc, and noVNC. Login is assisted: the CLI can open and fill the remote browser login form, but you still approve IBKR 2FA manually. The gateway and noVNC bind to loopback and should be reached through SSH tunnels only.
The assisted login CLI also refuses non-loopback login, API, and noVNC hosts to avoid sending credentials to the wrong place.

Start from an SSH session on the VPS:

```bash
git clone https://github.com/jeffscottward/ibkr-client-portal-docker.git
cd ibkr-client-portal-docker
sudo ./scripts/setup-kali-host.sh
sudo ./scripts/install-systemd.sh
sudo systemctl start ibkr-client-portal-docker-gateway
uv run ibkr-remote-login
```

From your laptop, tunnel the remote browser and gateway:

```bash
ssh -L 6080:127.0.0.1:6080 -L 5000:127.0.0.1:5000 user@your-vps
```

Then open `http://127.0.0.1:6080/vnc.html` locally if you need to watch or complete the login. See [docs/KALI_VPS.md](docs/KALI_VPS.md).

## Blog baseline example

After login:

```bash
uv run examples/aapl_contract_info.py
```

This mirrors the blog's AAPL contract metadata example against `https://localhost:5000/v1/api`.

## Notes

IBKR documents the Client Portal Gateway as local-machine software. Keep the browser login, gateway, and API client on this machine unless moving to a separately approved OAuth flow.

If the browser shows `Client login succeeds` but API calls still return `401 Unauthorized`, the login callback completed but the gateway did not expose an authenticated API session. Restart the gateway and retry at exactly `https://localhost:5000/`.

To override the default gateway zip:

```bash
IBKR_GATEWAY_ZIP_URL=https://download2.interactivebrokers.com/portal/clientportal.gw.zip ./start.sh
```

Stop the gateway with:

```bash
pm2 stop ibkr-client-portal-docker-gateway
pm2 delete ibkr-client-portal-docker-gateway
docker compose down
```

## License

MIT. See [LICENSE](LICENSE).
