# Kali VPS Setup

This guide assumes the VPS already exists and is already running Kali Linux. The repo does not provision Linode, choose a VPS plan, install Kali, or manage DNS.

## Network Model

- IBKR Client Portal Gateway listens on `https://localhost:5000/` on the VPS.
- noVNC listens on `http://127.0.0.1:6080/` on the VPS.
- Neither service should be exposed to the public internet.
- Access both through SSH port forwarding.

```bash
ssh -L 6080:127.0.0.1:6080 -L 5000:127.0.0.1:5000 user@your-vps
```

## Install Host Dependencies

On the VPS:

```bash
git clone https://github.com/jeffscottward/ibkr-client-portal-docker.git
cd ibkr-client-portal-docker
sudo ./scripts/setup-kali-host.sh
```

If the script adds your user to the `docker` group, log out and reconnect before running Docker commands as that user.
If you run behind a proxy, export `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY` before setup; the scripts pass them through to Docker and the gateway service.

## Install Gateway Service

```bash
sudo ./scripts/install-systemd.sh
sudo systemctl start ibkr-client-portal-docker-gateway
sudo systemctl status ibkr-client-portal-docker-gateway
```

Logs:

```bash
sudo journalctl -u ibkr-client-portal-docker-gateway -f
```

## Assisted Login

Run:

```bash
uv run ibkr-remote-login
```

The command prompts for username and password. The password is hidden and not stored. It opens Playwright-managed Chromium inside an Xvfb display and publishes the display through noVNC on loopback.

From your laptop, open:

```text
http://127.0.0.1:6080/vnc.html
```

Approve IBKR 2FA manually. The command waits until `/iserver/auth/status` reports `authenticated: true`, then exits.

## Read-Only Verification

```bash
uv run ibkr-read-only-check
```

The output redacts common token, user, account, session, IP, and hardware fields.

## Security Notes

- Do not pass passwords as CLI flags.
- Do not expose ports `5000`, `5900`, or `6080` publicly.
- Do not publish raw gateway logs from authenticated sessions.
- Use SSH tunnels and firewall rules that default-deny inbound traffic.
- The assisted login CLI refuses non-loopback login, API, and noVNC hosts.
- IBKR does not support fully automated Client Portal Gateway authentication; this flow keeps 2FA manual.

## Troubleshooting

- `docker: permission denied`: reconnect SSH after being added to the `docker` group, or run Docker commands with `sudo`.
- `Missing required command: Xvfb`: rerun `sudo ./scripts/setup-kali-host.sh`.
- Browser visible but API still returns `401`: restart the gateway service and retry login.
- noVNC does not load: confirm the SSH tunnel is active and the CLI printed `http://127.0.0.1:6080/vnc.html`.
